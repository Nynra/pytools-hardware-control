import piplates.DAQC2plate as DAQC2


class PulseWidthModulator:
    """Class for controlling the Pi-Plate DAQC2 pulse width modulation

    The Pi-Plate DAQC2 10bit pulse width modulation can be set to a specific frequency
    and duty cycle. The pulse width modulation can also be enabled or disabled.

    .. attention::

        Make sure DAC 1, 2, and 3 on the DAQC2 are not in use before using the
        pulse width modulation. This is not checked by this class.
    """

    def __init__(self, address: int) -> ...:
        """Initialize the PiPlatePulseWidthModulator object

        Parameters
        ----------
        address : int
            The address of the Pi-Plate DAQC2
        """
        if not isinstance(address, int):
            raise TypeError(f"Invalid address type: {type(address)}")
        if not DAQC2.VerifyADDR(address):
            raise ValueError(f"Invalid address: {address}")

        self._address = address
        self._channel_one_active = False
        self._channel_two_active = False
        self._channel_one_duty_cycle = 0
        self._channel_two_duty_cycle = 0


    # DUNDER METHODS
    def __repr__(self) -> str:
        return f"PiPlatePulseWidthModulator(address={self._address}, pin={self._pin})"
    
    def __str__(self) -> str:
        return f"PiPlatePulseWidthModulator at address {self._address} and pin {self._pin}"

    # PROPERTIES
    @property
    def address(self) -> int:
        """The address of the Pi-Plate DAQC2."""
        return self._address
    
    @property
    def channel_one_active(self) -> bool:
        """Whether the first channel is active."""
        return self._channel_one_active
    
    @channel_one_active.setter
    def channel_one_active(self, value: bool) -> ...:
        if not isinstance(value, bool):
            raise TypeError(f"Invalid type for channel_one_active: {type(value)}")
        
        self._channel_one_active = value
        self._reset_duty_cycle()
    
    @property
    def channel_two_active(self) -> bool:
        """Whether the second channel is active."""
        return self._channel_two_active
    
    @channel_two_active.setter
    def channel_two_active(self, value: bool) -> ...:
        if not isinstance(value, bool):
            raise TypeError(f"Invalid type for channel_two_active: {type(value)}")
        
        self._channel_two_active = value
        self._reset_duty_cycle()

    
    # PUBLIC FUNCTIONS
    def set_duty_cycle(self, channel: int, duty_cycle: int) -> ...:
        """Set the duty cycle of the pulse width modulation.

        Parameters
        ----------
        channel : int
            The channel to set the duty cycle for. Must be 1 or 2.
        duty_cycle : int
            The duty cycle to set. Must be between 0 and 1023.
        """
        if channel not in [1, 2]:
            raise ValueError(f"Invalid channel: {channel}")
        
        if duty_cycle < 0 or duty_cycle > 100:
            raise ValueError(f"Invalid duty cycle: {duty_cycle}")
        
        if channel == 1:
            self._channel_one_duty_cycle = duty_cycle
        else:
            self._channel_two_duty_cycle = duty_cycle

        self._reset_duty_cycle()

    # PRIVATE FUNCTIONS
    def _reset_duty_cycle(self) -> ...:
        """Reset the duty cycle of the pulse width modulation."""
        if self._channel_one_active:
            DAQC2.setPWM(self._address, 1, self._channel_one_duty_cycle)
        else:
            DAQC2.setPWM(self._address, 1, 0)

        if self._channel_two_active:
            DAQC2.setPWM(self._address, 2, self._channel_two_duty_cycle)
        else:
            DAQC2.setPWM(self._address, 2, 0)
