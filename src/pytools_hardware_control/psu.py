import serial
import time
from threading import Lock
from typing import Union
from .exceptions import (
    ConnectionError,
    TimeoutError,
    UnknownCommandError,
    ValueOutOfBoundsError,
    CurrentLimitError,
)


class DeltaPSU:
    """
    Class to control the Delta Elektronics PSU using the deltacode.ini protocol.

    The PSU is controlled using the pins on the backside of the device. Because we want
    to use python to remotely control the PSU an arduino is connected and used as a hardware
    controller. This class is mostly a wrapper to make communication with the arduino easier.
    """
    VOLTAGE_RANGE = (0, 30)
    CURRENT_RANGE = (0, 5)

    def __init__(
        self,
        port: str,
        baudrate: int = 9600,
        timeout: int = 1,
        connect_on_init: bool = True,
    ) -> ...:
        """
        Initialize the PSU controller.

        Parameters
        ----------
        port : str
            The serial port to connect to.
        baudrate : int
            The baudrate to use for the serial connection.
        timeout : int
            The timeout to use for the serial connection.
        connect_on_init : bool
            Whether to connect to the PSU on initialization.
        """
        if not isinstance(port, str):
            raise TypeError("port must be a string, not type {}".format(type(port)))
        if not isinstance(baudrate, int):
            raise TypeError(
                "baudrate must be an integer, not type {}".format(type(baudrate))
            )
        if not isinstance(timeout, int):
            raise TypeError(
                "timeout must be an integer, not type {}".format(type(timeout))
            )
        if not isinstance(connect_on_init, bool):
            raise TypeError(
                "connect_on_init must be a boolean, not type {}".format(
                    type(connect_on_init)
                )
            )

        self._port = port
        self._baudrate = baudrate
        self._timeout = timeout
        self._connect_on_init = connect_on_init
        self._lock = Lock()
        self._serial = None
        if self._connect_on_init:
            self.connect()

    # PROPERTIES
    @property
    def is_connected(self) -> bool:
        """Whether the PSU is connected or not."""
        try:
            return self.serial.is_open
        except AttributeError:
            return False

    # CONNECTION MANAGEMENT
    def connect(self) -> ...:
        if self.is_connected:
            return
        self._serial = serial.Serial(self._port, self._baudrate, timeout=self._timeout)

    def disconnect(self) -> ...:
        if not self.is_connected:
            return
        self._serial.close()
        self._serial = None

    # CONTROLLER COMMANDS
    def _send_and_receive(
        self,
        command: str,
        timeout: int = -1,
    ) -> Union[str, None]:
        """
        Send a command to the PSU and wait for a response.

        .. attention::
            This method does not typecheck and is prone to input errors. The
            user should not call this method directly.

        Parameters
        ----------
        command : str
            The command to send to the PSU.
        timeout : int
            The timeout to use for the serial connection.

        Returns
        -------
        response : str or None
            The response from the PSU.
        """
        if not self.is_connected:
            raise ConnectionError("Not connected to PSU")

        if timeout == -1:  # Use default
            timeout = self._timeout

        # Check if the command has a carriage return otherwise add it
        if command[-1] != "\r":
            command += "\r"

        # Get the threading lock
        if not self._lock.acquire(timeout=timeout):
            raise TimeoutError(
                "Timeout while waiting for PSU lock, it looks like the last command is not finished yet."
            )
        self._serial.write(command.encode())

        # Read the response
        etime = time.time() + timeout
        while time.time() < etime:
            if self.serial.in_waiting > 0:
                break
        else:
            self._lock.release()
            raise TimeoutError("Timeout while waiting for PSU response.")
        response = self.serial.readline().decode().strip()

        # Check if the response is an error or OK
        if response.startswith("err:"):
            self._lock.release()
            self._match_errors(response)
        elif response == "OK":
            response = None

        self._lock.release()
        return response

    def _match_errors(self, response: str) -> ...:
        """Find out what python error corresponds with the serial error."""
        # Error responses are formatted as :
        # err: <error_code> <error_message>
        response = response.split(" ")
        error_code = int(response[1])

        if error_code == 0:
            raise UnknownCommandError(response[2])
        elif error_code == 1:
            raise ValueOutOfBoundsError(response[2])
        elif error_code == 2:
            raise CurrentLimitError(response[2])
        elif error_code == 3:
            raise RuntimeError(response[2])
        else:
            raise RuntimeError(
                "Unknown error code {} returned by PSU".format(error_code)
            )

    def set_runmode(self) -> ...:
        """Set the PSU to run mode."""
        self._send_and_receive("r")

    def set_stopmode(self) -> ...:
        """Set the PSU to stop mode."""
        self._send_and_receive("s")

    # POWER SUPPLY MODE COMMANDS
    def set_voltage(self, voltage: float) -> ...:
        """
        Set the PSU voltage.

        Parameters
        ----------
        voltage : float
            The voltage to set.
        """
        if not isinstance(voltage, float):
            raise TypeError(
                "voltage must be a float, not type {}".format(type(voltage))
            )
        if not self.VOLTAGE_RANGE[0] <= voltage <= self.VOLTAGE_RANGE[1]:
            raise ValueError(
                "voltage must be between {} and {}, not {}".format(
                    self.VOLTAGE_RANGE[0], self.VOLTAGE_RANGE[1], voltage
                )
            )
        self._send_and_receive("sv {}".format(voltage * 1000))

    def get_voltage(self) -> float:
        """Get the PSU voltage."""
        return float(self._send_and_receive("gv") / 1000)

    def set_current(self, current: float) -> ...:
        """
        Set the PSU current.

        Parameters
        ----------
        current : float
            The current to set.
        """
        if not isinstance(current, float):
            raise TypeError(
                "current must be a float, not type {}".format(type(current))
            )
        if not self.CURRENT_RANGE[0] <= current <= self.CURRENT_RANGE[1]:
            raise ValueError(
                "current must be between {} and {}, not {}".format(
                    self.CURRENT_RANGE[0], self.CURRENT_RANGE[1], current
                )
            )
        self._send_and_receive("sc {}".format(current * 1000))

    def get_current(self) -> float:
        """Get the PSU current."""
        return float(self._send_and_receive("gc") / 1000)
