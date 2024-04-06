"""This module contains some base classes used in the daqc1 and 2 modules.

To make sure both modules are compatible, the base classes are defined here.
"""
from abc import ABC, abstractmethod
from typing import Union
from threading import Lock


class BaseDigitalInput(ABC):
    """Base class for a digital input pin."""

    @property
    @abstractmethod
    def pin(self) -> int:
        """The pin number of the digital input pin."""
        pass
    
    @property
    @abstractmethod
    def state(self) -> int:
        """The value read from the digital input pin."""
        pass

    @abstractmethod
    def read(self) -> bool:
        """Read the digital input pin."""
        pass


class BaseDigitalInterrupt(BaseDigitalInput):
    """Base class for a digital input pin with interrupt capabilities."""

    @property
    @abstractmethod
    def callback(self) -> Union[callable, None]:
        """The callback function to be called when the interrupt is triggered."""
        pass

    @property
    @abstractmethod
    def interrupt_enabled(self) -> bool:
        """Whether the interrupt is enabled."""
        pass

    @abstractmethod
    def enable_interrupt(self, callback: callable) -> ...:
        """Enable an interrupt on the digital input pin."""
        pass

    @abstractmethod
    def disable_interrupt(self) -> ...:
        """Disable the interrupt on the digital input pin."""
        pass


class BaseDigitalOutput(ABC):
    """Base class for a digital output pin."""

    @property
    @abstractmethod
    def pin(self) -> int:
        """The pin number of the digital output pin."""
        pass

    @property
    @abstractmethod
    def state(self) -> int:
        """Get or set the state of the digital output pin."""
        pass

    @state.setter
    @abstractmethod
    def state(self, value: int) -> ...:
        pass

    @abstractmethod
    def write(self, value: int) -> ...:
        """Write a value to the digital output pin."""
        pass


class BaseAnalogInput(ABC):
    """Base class for an analog input pin."""

    @property
    @abstractmethod
    def pin(self) -> int:
        """The pin number of the analog input pin."""
        pass

    @property
    @abstractmethod
    def value(self) -> float:
        """The value read from the analog input pin."""
        pass

    @abstractmethod
    def read(self) -> float:
        """Read the analog input pin."""
        pass


class BaseAnalogOutput(ABC):
    """Base class for an analog output pin."""

    @property
    @abstractmethod
    def pin(self) -> int:
        """The pin number of the analog output pin."""
        pass

    @property
    @abstractmethod
    def value(self) -> float:
        """Get or set the value of the analog output pin."""
        pass

    @value.setter
    @abstractmethod
    def value(self, value: float) -> ...:
        pass

    @abstractmethod
    def write(self, value: float) -> ...:
        """Write a value to the analog output pin."""
        pass


class BasePlate(ABC):
    """Base class for a plate."""

    @property
    @abstractmethod
    def address(self) -> int:
        """The address of the plate."""
        pass

    @property
    @abstractmethod
    def firmware_version(self) -> str:
        """The firmware version of the plate."""
        pass

    @property
    @abstractmethod
    def hardware_version(self) -> str:
        """The hardware version of the plate."""
        pass

    @abstractmethod
    def get_digital_input(self, pin: int) -> BaseDigitalInput:
        """Get a digital input pin."""
        pass

    @abstractmethod
    def get_digital_output(self, pin: int) -> BaseDigitalOutput:
        """Get a digital output pin."""
        pass

    @abstractmethod
    def get_analog_input(self, pin: int) -> BaseAnalogInput:
        """Get an analog input pin."""
        pass

    @abstractmethod
    def get_analog_output(self, pin: int) -> BaseAnalogOutput:
        """Get an analog output pin."""
        pass

    @abstractmethod
    def read_adc(self, channel: int) -> float:
        """Read the analog input pin."""
        pass

    @abstractmethod
    def read_all_adcs(self) -> list[float]:
        """Read all analog input pins."""
        pass


class PinRegister:
    """Class for keeping track of which pins are used"""

    def __init__(self) -> ...:
        self._lock = Lock()
        self._digital_inputs = 7
        self._digital_outputs = 7
        self._analog_inputs = 7
        self._analog_outputs = 3

        self._pins = {
            "digital_inputs": [],
            "digital_outputs": [],
            "analog_inputs": [],
            "analog_outputs": [],
        }

    def register_digital_input(self, pin: int) -> ...:
        """Register a digital input pin"""
        if not (0 <= pin <= self._digital_inputs):
            raise ValueError(f"Invalid pin: {pin}")
        if pin in self._pins["digital_inputs"]:
            raise ValueError(f"Pin {pin} is already registered")
        with self._lock:
            self._pins["digital_inputs"].append(pin)

    def register_digital_output(self, pin: int) -> ...:
        """Register a digital output pin"""
        if not (0 <= pin <= self._digital_outputs):
            raise ValueError(f"Invalid pin: {pin}")
        if pin in self._pins["digital_outputs"]:
            raise ValueError(f"Pin {pin} is already registered")
        with self._lock:
            self._pins["digital_outputs"].append(pin)

    def register_analog_input(self, pin: int) -> ...:
        """Register an analog input pin"""
        if not (0 <= pin <= self._analog_inputs):
            raise ValueError(f"Invalid pin: {pin}")
        if pin in self._pins["analog_inputs"]:
            raise ValueError(f"Pin {pin} is already registered")
        with self._lock:
            self._pins["analog_inputs"].append(pin)

    def register_analog_output(self, pin: int) -> ...:
        """Register an analog output pin"""
        if not (1 <= pin <= self._analog_outputs):
            raise ValueError(f"Invalid pin: {pin}")
        if pin in self._pins["analog_outputs"]:
            raise ValueError(f"Pin {pin} is already registered")
        with self._lock:
            self._pins["analog_outputs"].append(pin)

    def unregister_digital_input(self, pin: int) -> ...:
        """Unregister a digital input pin"""
        with self._lock:
            self._pins["digital_inputs"].remove(pin)

    def unregister_digital_output(self, pin: int) -> ...:
        """Unregister a digital output pin"""
        with self._lock:
            self._pins["digital_outputs"].remove(pin)

    def unregister_analog_input(self, pin: int) -> ...:
        """Unregister an analog input pin"""
        with self._lock:
            self._pins["analog_inputs"].remove(pin)

    def unregister_analog_output(self, pin: int) -> ...:
        """Unregister an analog output pin"""
        with self._lock:
            self._pins["analog_outputs"].remove(pin)

    def get_pins(self) -> dict:
        """Get all registered pins"""
        with self._lock:
            return self._pins
