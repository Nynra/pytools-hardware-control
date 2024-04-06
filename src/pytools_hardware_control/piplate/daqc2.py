"""
DAQC2 module
============

This module contains classes for controlling the Pi-Plate DAQC2

The Pi-Plate DAQC2 is a data acquisition and control board for the Raspberry Pi.
The following pins can be found on the board:
- Digital inputs: 0-7
- Open drain digital outputs: 0-7
- 5VDC output: 1
- +/- 12V 16bit ADC: 0-7
- 12bit DAC: 1-3
- Auxillary 5VDC input: 1
- Frequency input: 1
- 10bit Pulse width modulation output: 1-3

Digital pins
------------

Multiple DACQ boards can be stacked on top of each other, each with a unique
address. The address can be set using the jumpers on the board. The board supplies
eight open drain digital outputs (max 3A) and a flyback protection terminal for inductive loads.
To obtain a simple digital signal from the digital outputs, a pull-up resistor is
required (4.7kΩ between output pin and ground).
"""

from ..exceptions import MachineTypeError

try:
    import RPi.GPIO as GPIO
except ImportError:
    raise MachineTypeError("This module can only be run on a Raspberry Pi")

import piplates.DAQC2plate as DAQC2
from .base import (
    BaseDigitalInput,
    BaseDigitalOutput,
    BaseAnalogInput,
    BaseAnalogOutput,
    BasePlate,
    PinRegister,
)


class DAQC2plate(BasePlate):
    """Class for controlling the Pi-Plate DAQC2.

    The goal of this class is to keep track of which pins are used and prevent
    conflicts. The class also provides methods to control the digital and analog
    pins on the Pi-Plate DAQC2.
    """

    def __init__(self, address: int) -> ...:
        """Initialize the PiPlateDAQC2 object

        Parameters
        ----------
        address : int
            The address of the Pi-Plate DAQC2
        """
        if not isinstance(address, int):
            raise TypeError(
                f"Invalid address type, expected int but got {type(address)}"
            )
        if not DAQC2.VerifyADDR(address):
            raise ValueError(f"Invalid address: {address}")
        self._address = address
        self._pin_register = PinRegister()

    # DUNDER METHODS
    def __repr__(self) -> str:
        return f"PiPlateDAQC2(address={self._address})"

    def __str__(self) -> str:
        return f"PiPlateDAQC2 at address {self._address}"

    # PROPERTIES
    @property
    def address(self) -> int:
        """Get the address of the Pi-Plate DAQC2"""
        return self._address

    @property
    def firmware_version(self) -> str:
        """Get the firmware version of the Pi-Plate DAQC2"""
        return DAQC2.getFWrev(self._address)

    @property
    def hardware_version(self) -> str:
        """Get the hardware version of the Pi-Plate DAQC2"""
        return DAQC2.getHWrev(self._address)

    # PUBLIC FUNCTIONS
    def get_digital_input(self, pin: int) -> "DAQC2plate.DigitalInput":
        """Get a digital input object"""
        if not isinstance(pin, int):
            raise TypeError(f"Invalid pin type, expected int but got {type(pin)}")
        if DAQC2.VerifyDINchannel(pin):
            raise ValueError(f"Invalid pin: {pin}")
        self._pin_register.register_digital_input(pin)
        return self.DigitalInput(self._address, pin)

    def get_digital_output(self, pin: int) -> "DAQC2plate.DigitalOutput":
        """Get a digital output object"""
        self._pin_register.register_digital_output(pin)
        return self.DigitalOutput(self._address, pin)

    def get_analog_input(self, pin: int) -> "DAQC2plate.AnalogInput":
        """Get an analog input object"""
        self._pin_register.register_analog_input(pin)
        return self.AnalogInput(self._address, pin)

    def get_analog_output(self, pin: int) -> "DAQC2plate.AnalogOutput":
        """Get an analog output object"""
        self._pin_register.register_analog_output(pin)
        return self.AnalogOutput(self._address, pin)

    def read_adc(self, channel: int) -> int:
        """Read the analog-to-digital converter on the Pi-Plate DAQC2

        Parameters
        ----------
        channel : int
            The channel to read the ADC from

        Returns
        -------
        int
            The ADC value
        """
        if not isinstance(channel, int):
            raise TypeError(
                f"Invalid channel type, expected int but got {type(channel)}"
            )
        if DAQC2.VerifyAINchannel(channel):
            raise ValueError(f"Invalid channel: {channel}")
        return DAQC2.getADC(self._address, channel)

    def read_all_adcs(self) -> list[int]:
        """Read all analog-to-digital converters on the Pi-Plate DAQC2

        Returns
        -------
        list
            The ADC values
        """
        return DAQC2.getADCall(self._address)

    def read_dac(self, channel: int) -> int:
        """Read the digital-to-analog converter on the Pi-Plate DAQC2

        Parameters
        ----------
        channel : int
            The channel to read the DAC from

        Returns
        -------
        int
            The DAC value
        """
        if not isinstance(channel, int):
            raise TypeError(
                f"Invalid channel type, expected int but got {type(channel)}"
            )
        if not DAQC2.VerifyFGchannel(channel):
            raise ValueError(f"Invalid channel: {channel}")
        return DAQC2.getDAC(self._address, channel)

    class DigitalInput(BaseDigitalInput):
        """Class for controlling a digital pin on the Pi-Plate DAQC2"""

        def __init__(self, address: int, pin: int) -> ...:
            """Initialize the PiPlateDigitalInput object

            Parameters
            ----------
            address : int
                The address of the Pi-Plate DAQC2
            pin : int
                The pin number of the digital input pin
            """
            if not isinstance(address, int):
                raise TypeError(
                    f"Invalid address type, expected int but got {type(address)}"
                )
            if not isinstance(pin, int):
                raise TypeError(f"Invalid pin type, expected int but got {type(pin)}")
            if not DAQC2.VerifyADDR(address):
                raise ValueError(f"Invalid address: {address}")
            if not DAQC2.VerifyDINchannel(pin):
                raise ValueError(f"Invalid pin: {pin}")

            self._address = address
            self._pin = pin

        # PROPERTIES
        @property
        def pin(self) -> int:
            """Get the pin number of the digital input pin"""
            return self._pin

        @property
        def state(self) -> bool:
            """Get the state of the digital input pin"""
            return True if DAQC2.getDINbit(self._address, self._pin) == 1 else False

        def read(self) -> bool:
            """Read the digital input pin"""
            return self.state

    class DigitalOutput(BaseDigitalOutput):
        """Class for controlling a digital pin on the Pi-Plate DAQC2

        To obtain a simple digital signal from the digital outputs, a pull-up resistor is
        required (4.7kΩ between output pin and ground).

        .. attention::

            When using a pullup resistor the signal will be inverted. A high signal will
            be read as a low signal and vice versa.

        """

        def __init__(self, address: int, pin: int) -> ...:
            """Initialize the PiPlateDigitalOutput object

            Parameters
            ----------
            address : int
                The address of the Pi-Plate DAQC2
            pin : int
                The pin number of the digital output pin
            """
            if not isinstance(address, int):
                raise TypeError(
                    f"Invalid address type, expected int but got {type(address)}"
                )
            if not isinstance(pin, int):
                raise TypeError(f"Invalid pin type, expected int but got {type(pin)}")
            if not DAQC2.VerifyADDR(address):
                raise ValueError(f"Invalid address: {address}")
            if not DAQC2.VerifyDOUTchannel(pin):
                raise ValueError(f"Invalid pin: {pin}")

            self._address = address
            self._pin = pin
            self._state = False

        # PROPERTIES
        @property
        def pin(self) -> int:
            """Get the pin number of the digital output pin"""
            return self._pin

        @property
        def state(self) -> bool:
            """Get or set the state of the digital output pin.

            Parameters
            ----------
            state : bool
                The state the pin should be set to

            Returns
            -------
            bool
                The state of the digital output pin
            """
            return self._state

        @state.setter
        def state(self, state: bool) -> ...:
            if not isinstance(state, bool):
                raise TypeError(
                    f"Invalid state type, expected bool but got {type(state)}"
                )
            DAQC2.setDOUTbit(self._address, self._pin, 1 if state else 0)
            self._state = state

        def write(self, value: bool) -> ...:
            """Write a value to the digital output pin"""
            if not isinstance(value, bool):
                raise TypeError(
                    f"Invalid value type, expected bool but got {type(value)}"
                )
            self.state = value

    class AnalogInput(BaseAnalogInput):
        """Class for controlling an analog pin on the Pi-Plate DAQC2"""

        def __init__(self, address: int, pin: int) -> ...:
            """Initialize the PiPlateAnalogInput object

            Parameters
            ----------
            address : int
                The address of the Pi-Plate DAQC2
            pin : int
                The pin number of the analog input pin
            """
            if not isinstance(address, int):
                raise TypeError(
                    f"Invalid address type, expected int but got {type(address)}"
                )
            if not isinstance(pin, int):
                raise TypeError(f"Invalid pin type, expected int but got {type(pin)}")
            if not DAQC2.VerifyADDR(address):
                raise ValueError(f"Invalid address: {address}")
            if not DAQC2.VerifyAINchannel(pin):
                raise ValueError(f"Invalid pin: {pin}")

            self._address = address
            self._pin = pin

        # PROPERTIES
        @property
        def pin(self) -> int:
            """Get the pin number of the analog input pin"""
            return self._pin

        @property
        def value(self) -> float:
            """Get the value read from the analog input pin"""
            return DAQC2.getADC(self._address, self._pin)

        def read(self) -> float:
            """Read the analog input pin"""
            return self.value

    class AnalogOutput(BaseAnalogOutput):
        """Class for controlling an analog pin on the Pi-Plate DAQC2"""

        def __init__(self, address: int, pin: int) -> ...:
            """Initialize the PiPlateAnalogOutput object

            Parameters
            ----------
            address : int
                The address of the Pi-Plate DAQC2
            pin : int
                The pin number of the analog output pin
            """
            if not isinstance(address, int):
                raise TypeError(
                    f"Invalid address type, expected int but got {type(address)}"
                )
            if not isinstance(pin, int):
                raise TypeError(f"Invalid pin type, expected int but got {type(pin)}")
            if not DAQC2.VerifyADDR(address):
                raise ValueError(f"Invalid address: {address}")
            if not DAQC2.VerifyFGchannel(pin):
                raise ValueError(f"Invalid pin: {pin}")

            self._address = address
            self._pin = pin

        # PROPERTIES
        @property
        def pin(self) -> int:
            """Get the pin number of the analog output pin"""
            return self._pin

        @property
        def value(self) -> int:
            """Get or set the value of the analog output pin.

            Parameters
            ----------
            value : int
                The value to write to the analog output pin

            Returns
            -------
            int
                The value of the analog output pin
            """
            return DAQC2.getDAC(self._address, self._pin)

        @value.setter
        def value(self, value: int) -> ...:
            if not isinstance(value, int):
                raise TypeError(
                    f"Invalid value type, expected int but got {type(value)}"
                )
            if not (0 <= value <= 4095):
                raise ValueError(f"Invalid value: {value}")
            DAQC2.setDAC(self._address, self._pin, value)

        def write(self, value: int) -> ...:
            """Write a value to the analog output pin"""
            self.value = value
