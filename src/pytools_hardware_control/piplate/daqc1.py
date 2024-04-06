"""This module contains functions and classes to control the DAQC1 plate.

The DAQC1 plate is a digital and analog input/output plate for the Raspberry Pi.
The following pins can be found on the board:
- 350mA 12VDC max Open drain digital outputs: 7
- Digital inputs (3.3 and 5V compatible): 8
- 10bit 4.096V 1Khz max ADC: 8
- 10bit 4.096V DAC: 2
- 10bit PWM outputs: 2
- Auxiliary power input (5V): 1
"""

from ..exceptions import MachineTypeError

try:
    import RPi.GPIO as GPIO
except ImportError:
    raise MachineTypeError("This module is only available on a Raspberry Pi.")

import piplates.DAQCplate as DAQC
from typing import Union
from .base import (
    BaseDigitalInput,
    BaseDigitalInterrupt,
    BaseDigitalOutput,
    BaseAnalogInput,
    BaseAnalogOutput,
    BasePlate,
    PinRegister,
)


class DAQCplate(BasePlate):
    """Class to control the DAQC1 plate."""

    def __init__(self, address: int = 0) -> ...:
        """
        Initialize the DAQC1 plate.

        Parameters
        ----------
        address : int
            The address of the DAQC1 plate.
        """
        if not isinstance(address, int):
            raise TypeError(
                "address must be an integer, not type {}".format(type(address))
            )
        if not DAQC.VerifyADDR(address):
            raise ValueError("Invalid address for DAQC1 plate.")
        self._address = address
        self._pin_register = PinRegister()

    # DUNDER METHODS
    def __repr__(self) -> str:
        """Return the string representation of the DAQC1 plate."""
        return f"DAQC1 plate at address {self._address}"

    def __str__(self) -> str:
        """Return the string representation of the DAQC1 plate."""
        return f"DAQC1 plate at address {self._address}"
    
    # PROPERTIES
    @property
    def address(self) -> int:
        """The address of the DAQC1 plate."""
        return self._address
    
    @property
    def firmware_version(self) -> str:
        """The firmware version of the DAQC1 plate."""
        return DAQC.getFWrev(self._address)
    
    @property
    def hardware_version(self) -> str:
        """The hardware version of the DAQC1 plate."""
        return DAQC.getHWrev(self._address)

    # PUBLIC METHODS
    def get_digital_input(self, pin: int) -> "DAQCplate.DigitalInput":
        """Return a digital input pin object."""
        if not isinstance(pin, int):
            raise TypeError("pin must be an integer, not type {}".format(type(pin)))
        if not DAQC.VerifyDINchannel(pin):
            raise ValueError("Invalid pin number for digital input.")
        self._pin_register.register_digital_input(pin)
        return self.DAQCdigitalInput(self._address, pin)

    def get_digital_output(self, pin: int) -> "DAQCplate.DigitalOutput":
        """Return a digital output pin object."""
        if not isinstance(pin, int):
            raise TypeError("pin must be an integer, not type {}".format(type(pin)))
        if not DAQC.VerifyDOUTchannel(pin):
            raise ValueError("Invalid pin number for digital output.")
        self._pin_register.register_digital_output(pin)
        return self.DAQCdigitalOutput(self._address, pin)

    def get_analog_input(self, pin: int) -> "DAQCplate.AnalogInput":
        """Return an analog input pin object."""
        if not isinstance(pin, int):
            raise TypeError("pin must be an integer, not type {}".format(type(pin)))
        if not DAQC.VerifyAINchannel(pin):
            raise ValueError("Invalid pin number for analog input.")
        self._pin_register.register_analog_input(pin)
        return self.DAQCanalogInput(self._address, pin)

    def get_analog_output(self, pin: int) -> "DAQCplate.AnalogOutput":
        """Return an analog output pin object."""
        if not isinstance(pin, int):
            raise TypeError("pin must be an integer, not type {}".format(type(pin)))
        if not DAQC.VerifyAOUTchannel(pin):
            raise ValueError("Invalid pin number for analog output.")
        self._pin_register.register_analog_output(pin)
        return self.DAQCAnalogOutput(self._address, pin)
    
    def read_adc(self, channel: int) -> float:
        """Read the analog input pin."""
        if not isinstance(channel, int):
            raise TypeError(
                "channel must be an integer, not type {}".format(type(channel))
            )
        if not DAQC.VerifyAINchannel(channel):
            raise ValueError("Invalid channel for analog input.")
        return DAQC.getADC(self._address, channel)
    
    def read_all_adcs(self) -> list[float]:
        """Read all analog input pins."""
        return DAQC.getADCall(self._address)

    # NESTED CLASSES
    class DigitalInput(BaseDigitalInput):
        """Class to control a digital input pin on the DAQC1 plate."""

        def __init__(self, address: int, pin: int) -> ...:
            """
            Initialize the digital input pin.

            Parameters
            ----------
            address : int
                The address of the DAQC1 plate.
            pin : int
                The pin number of the digital input.
            """
            if not isinstance(address, int):
                raise TypeError(
                    "address must be an integer, not type {}".format(type(address))
                )
            if not isinstance(pin, int):
                raise TypeError("pin must be an integer, not type {}".format(type(pin)))
            self._address = address
            self._pin = pin

        @property
        def pin(self) -> int:
            """The pin number of the digital input."""
            return self._pin

        @property
        def state(self) -> bool:
            """The state of the digital input."""
            return DAQC.getDINbit(self._address, self._pin)

        def read(self) -> bool:
            """Read the digital input."""
            return self.state

    class DigitalOutput(BaseDigitalOutput):
        """Class to control a digital output pin on the DAQC1 plate."""

        def __init__(self, address: int, pin: int) -> ...:
            """
            Initialize the digital output pin.

            Parameters
            ----------
            address : int
                The address of the DAQC1 plate.
            pin : int
                The pin number of the digital output.
            """
            if not isinstance(address, int):
                raise TypeError(
                    "address must be an integer, not type {}".format(type(address))
                )
            if not isinstance(pin, int):
                raise TypeError("pin must be an integer, not type {}".format(type(pin)))
            if not DAQC.VerifyDOUTchannel(pin):
                raise ValueError("Invalid pin number for digital output.")

            self._address = address
            self._pin = pin

        @property
        def pin(self) -> int:
            """The pin number of the digital output."""
            return self._pin

        @property
        def state(self) -> bool:
            """The state of the digital output."""
            return DAQC.getDOUTbit(self._address, self._pin)

        @state.setter
        def state(self, value: bool) -> ...:
            DAQC.setDOUTbit(self._address, self._pin, value)

        def write(self, value: bool) -> ...:
            """Write a value to the digital output."""
            self.state = value

    class AnalogInput(BaseAnalogInput):
        """Class to control an analog input pin on the DAQC1 plate."""

        def __init__(self, address: int, pin: int) -> ...:
            """
            Initialize the analog input pin.

            Parameters
            ----------
            address : int
                The address of the DAQC1 plate.
            pin : int
                The pin number of the analog input.
            """
            if not isinstance(address, int):
                raise TypeError(
                    "address must be an integer, not type {}".format(type(address))
                )
            if not isinstance(pin, int):
                raise TypeError("pin must be an integer, not type {}".format(type(pin)))
            if not DAQC.VerifyAINchannel(pin):
                raise ValueError("Invalid pin number for analog input.")

            self._address = address
            self._pin = pin

        @property
        def pin(self) -> int:
            """The pin number of the analog input."""
            return self._pin

        @property
        def value(self) -> float:
            """The value read from the analog input."""
            return DAQC.getADC(self._address, self._pin)

        def read(self) -> float:
            """Read the analog input."""
            return self.value

    class AnalogOutput(BaseAnalogOutput):
        """Class to control an analog output pin on the DAQC1 plate."""

        def __init__(self, address: int, pin: int) -> ...:
            """
            Initialize the analog output pin.

            Parameters
            ----------
            address : int
                The address of the DAQC1 plate.
            pin : int
                The pin number of the analog output.
            """
            if not isinstance(address, int):
                raise TypeError(
                    "address must be an integer, not type {}".format(type(address))
                )
            if not isinstance(pin, int):
                raise TypeError("pin must be an integer, not type {}".format(type(pin)))
            if not DAQC.VerifyAOUTchannel(pin):
                raise ValueError("Invalid pin number for analog output.")

            self._address = address
            self._pin = pin

        @property
        def pin(self) -> int:
            """The pin number of the analog output."""
            return self._pin

        @property
        def value(self) -> float:
            """The value of the analog output."""
            return DAQC.getDAC(self._address, self._pin)

        @value.setter
        def value(self, value: float) -> ...:
            DAQC.setDAC(self._address, self._pin, value)

        def write(self, value: float) -> ...:
            """Write a value to the analog output."""
            self.value = value
