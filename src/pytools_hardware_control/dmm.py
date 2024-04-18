import serial
import time
from .exceptions import ConnectionError, TimeoutError
from threading import Thread, Lock


class TTI1604:
    """Read a TTI1604 DDM with Python.

    20231102
    initial release of the script. Working, but not documented / optimised yet.

    Connect the device and set the serial port. After that use the commands:

    .. code-block:: python

        # Send a binary string (b'a' for example) to the device. 
        # Commands are the key-presses as if pressed on the device.
        instance.send_command(ser, command, debug=False)
        
        # Reads the data from the serial bus and stores the (10 characters) in char.
        char = instance.read_data(ser)

        # Parse the readout and returns the number from the display. If resistance is
        # measured the kOhm or Ohm settings are taking into account.
        char = instance.parse_number_unit(char)
        
        # Parse all the data in the 10-char string from the device.
        # All settings are retreived.
        char = instance.parse_data(char)
        

    Available keys:
    * Keys
    * Key Up = 'a'
    * Key Down = 'b'
    * Key Auto = 'c'
    * Key A = 'd'
    * Key mA = 'e'
    * Key V = 'f'
    * Key Operate = 'g'
    * Key W = 'i'
    * Key Hz = 'j'
    * Key Shift = 'k'
    * Key AC = 'l'
    * Key DC = 'm'
    * Key mV = 'n'
    * Set remote mode = 'u'
    * Set local mode = 'v'
    """

    def __init__(
        self,
        serial_port: str = "/dev/ttyUSB1",
        baudrate: int = 9600,
        timeout: int = 1,
        verbose: bool = True,
        debug: bool = True,
        connect_on_init: bool = True,
    ) -> ...:
        """Initialize the TTI1604 class."""
        self._debug = debug
        self._verbose = verbose
        self._serial_port = serial_port
        self._baudrate = baudrate
        self._lock = Lock()

        # Initialize serial connection
        if connect_on_init:
            self.connect(timeout=timeout)

        else:
            self._ser = None
            if verbose:
                print(
                    "Not connecting on init, user should call connect before using the instrument."
                )

    # PROPERTIES
    @property
    def serial_port(self) -> str:
        """The serial port used to connect to the TTI1604."""
        return self._serial_port

    @property
    def is_connected(self) -> bool:
        """Returns True if the serial connection is open."""
        try:
            return self._ser.is_open
        except AttributeError:
            return False

    @property
    def debug(self) -> bool:
        """Returns True if debug mode is enabled."""
        return self._debug

    @debug.setter
    def debug(self, value: bool) -> ...:
        """Set debug mode."""
        self._debug = value

    # CONNECTION METHODS
    def connect(self, timeout: int = 10) -> ...:
        """Connect to the TTI1604.

        Parameters
        ----------
        timeout : int
            The time in seconds to wait for a connection.

        Raises
        ------
        ConnectionError
            Raised when a connection to the TTI1604 cannot be established.
        """
        # Check if not already connected
        if self.is_connected:
            if self._verbose:
                print(
                    "Already connected to TTI1604 on port {}.".format(self.serial_port)
                )
            return

        # Open connection
        self._ser = serial.Serial(
            self._serial_port, baudrate=self._baudrate, dsrdtr=0, timeout=1
        )
        self._ser.rts = 0
        self._ser.dtr = 1

        # # Wait for connection confirmation
        # retval = False
        # etime = time.time() + timeout
        # while not retval and time.time() < etime:
        #     retval = self.send_command(b"u")

        # if retval:
        #     if self._verbose:
        #         print("Connected to TTI1604 on port {}.".format(self._serial_port))
        # else:
        #     raise ConnectionError(
        #         "Could not connect to TTI1604 on port {} within the set time {}s.".format(
        #             self._serial_port, timeout
        #         )
        #     )

    # COMMUNICATION METHODS
    def send_command(self, command: str, timeout:int=5) -> bool:
        """Send a command to the TTI1604.

        Parameters
        ----------
        command : str
            The command to send to the TTI1604.
        timeout : int, optional
            The time in seconds to wait for the threading lock
            to be acquired. The default is 5s.

        Returns
        -------
        bool
            True if the command was executed, False otherwise.
        """
        # cleanup state
        if not self._lock.acquire(timeout=timeout):
            raise TimeoutError("Could not acquire lock within {}s.".format(timeout))
        self._ser.reset_input_buffer()
        self._ser.reset_output_buffer()

        # send command
        self._ser.write(command)
        time.sleep(0.3)  # max timeout
        ret = self._ser.read(10)

        # check if command was executed
        retval = False
        if len(ret) == 1:
            ret = chr(ret[0])
        if self._debug or self._verbose:
            print(ret, command.decode())
        if ret == command.decode():
            retval = True

        if self._debug or self._verbose:
            if retval:
                print("Command ok")
            else:
                print("Command not ok: ", command, " ", ret)
        self._lock.release()
        return retval

    def read_data(self, timeout:float = 5) -> bytes:
        """Read data from the TTI1604.

        Parameters
        ----------
        timeout : float, optional
            The time in seconds to wait for the threading lock
            to be acquired. The default is 5s.

        Returns
        -------
        bytes
            The data read from the TTI1604.
        """
        if not self.is_connected:
            raise ConnectionError("Not connected to TTI1604, call connect() first.")
        if not self._lock.acquire(timeout=timeout):
            raise TimeoutError("Could not acquire lock within {}s.".format(timeout))
        self._ser.reset_input_buffer()
        self._ser.reset_output_buffer()
        value = self._ser.read(10)
        self._lock.release()
        return value

    def parse_number(self, char: str) -> float:
        """Parse the number from the readout.

        Parameters
        ----------
        char : str
            The readout from the TTI1604.

        Returns
        -------
        float
            The number from the readout.
        """
        keys = {
            252: "0",
            253: "0.",
            96: "1",
            97: "1.",
            218: "2",
            219: "2.",
            242: "3",
            243: "3.",
            102: "4",
            103: "4.",
            182: "5",
            183: "5.",
            190: "6",
            191: "6.",
            224: "7",
            225: "7.",
            254: "8",
            256: "8.",
            230: "9",
            231: "9.",
            238: "A",
            156: "C",
            122: "D",
            158: "E",
            142: "F",
            140: "R",
            30: "T",
            124: "U",
            28: "L",
            0: "",
            2: "",
        }

        # Convert the string to a number?
        val = ""
        if char[3] & 1 << 0 != 0:
            val = "-"
        for ii in range(4, 9):
            if char[ii] in keys.keys():
                val += keys[char[ii]]

        # check if number is float
        try:
            val = float(val)
        except ValueError:
            pass
        return val

    def parse_number_unit(self, char: str) -> float:
        """Parse the number and unit from the readout.

        Parameters
        ----------
        char : str
            The readout from the TTI1604.

        Returns
        -------
        float
            The number from the readout.
        """
        val = self.parse_number(char)
        dmm_range = (char[1] & ((1 << 7) - 1)) >> 4
        dmm_type = char[1] & ((1 << 3) - 1)  # last 3 bits
        if isinstance(val, float) and (dmm_type == 5) and (dmm_range != 0):
            val = val * 1000
        return val

    def parse_data(self, char: str) -> dict:
        """Parse the data from the readout.

        Parameters
        ----------
        char : str
            The readout from the TTI1604.

        Returns
        -------
        dict
            A dictionary containing the parsed data.
        """
        range_type_info = {
            1: "mV",
            2: "V",
            3: "mA",
            4: "A",
            5: "Ohm",
            6: "Continuity",
            7: "Diode Test",
        }
        range_info = {
            0: "400 Ohm",
            1: "4 kOhm / 4 Vac / 4 Vdc / 4 mAdc / 1 mAac",
            2: "40 kOhm / 40 Vac / 40 Vdc / 10 Adc / 10 Aac",
            3: "400 kOhm / 400 Vac / 400 Vdc / 400 mAdc / 400 mAac / 400 mVdc / 400 mVac",
            4: "4 MOhm / 750 Vac / 1000 Vdc",
            5: "40 MOhm",
        }
        acdc = {0: "DC", 1: "AC"}

        # Parse all the data
        if char[0] != 13:  # else no data
            return False
        dmm_type = char[1] & ((1 << 3) - 1)  # last 3 bits
        dmm_acdc = (char[1] & ((1 << 4) - 1)) >> 3  # 1 AC, 0 DC
        dmm_range = (char[1] & ((1 << 7) - 1)) >> 4
        thold = char[2] & 1 != 0
        minmax = char[2] & 1 << 2 != 0
        hertz = char[2] & 1 << 4 != 0
        null = char[2] & 1 << 5 != 0
        auto = char[2] & 1 << 6 != 0
        minus = char[3] & 1 << 0 != 0
        doublebeep = char[9] & 1 != 0
        autorange = char[9] & 1 << 2 != 0
        contbuzz = char[9] & 1 << 3 != 0
        dispmin = char[9] & 1 << 4 != 0
        dispmax = char[9] & 1 << 5 != 0
        disphold = char[9] & 1 << 6 != 0
        gate10sec = char[9] & 1 << 7 != 0
        val = self.parse_number_unit(char)

        # Print if needed
        if self._verbose or self._debug:
            print(
                "_______________________________________________________________________"
            )
            print(range_type_info[dmm_type], acdc[dmm_acdc], range_info[dmm_range])
            print("Thold: ", thold)
            print("MinMax: ", minmax)
            print("Hertz: ", hertz)
            print("NULL: ", null)
            print("Auto: ", auto)
            print("DoubleBeep: ", doublebeep)
            print("AutoRangeSet : ", autorange)
            print("Cont Buz : ", contbuzz)
            print("Disp Min : ", dispmin)
            print("Disp Max : ", dispmax)
            print("Disp Hold : ", disphold)
            print("Gate 10 sec : ", gate10sec)
            print("value: ", val)
            print(
                "_______________________________________________________________________"
            )

        # Return the state dict
        return {
            "type": range_type_info[dmm_type],
            "acdc": acdc[dmm_acdc],
            "range": range_info[dmm_range],
            "thold": thold,
            "minmax": minmax,
            "hertz": hertz,
            "null": null,
            "auto": auto,
            "doublebeep": doublebeep,
            "autorange": autorange,
            "contbuzz": contbuzz,
            "dispmin": dispmin,
            "dispmax": dispmax,
            "disphold": disphold,
            "gate10sec": gate10sec,
            "value": val,
        }

    def get_complete_state(self) -> dict:
        """Get the state of the TTI1604.

        Returns
        -------
        dict
            A dictionary containing the state of the TTI1604.
        """
        if not self.is_connected:
            raise ConnectionError("Not connected to TTI1604, call connect() first.")
        return self.parse_data(self.read_data())

    def get_value(self) -> float:
        """Get the value of the TTI1604.

        Returns
        -------
        float
            The value of the TTI1604.
        """
        if not self.is_connected:
            raise ConnectionError("Not connected to TTI1604, call connect() first.")
        return self.parse_number_unit(self.read_data())


if __name__ == "__main__":
    dmm = TTI1604()
    dmm.send_command(b"e")  # mA
    dmm.send_command(b"l")  # AC

    # Get the DMM state
    state = dmm.get_complete_state()
    print(state)

    # Get the DMM value
    val = dmm.get_value()
    print(val)
