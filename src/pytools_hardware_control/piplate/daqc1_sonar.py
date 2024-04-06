import piplates.DAQCplate as DAQC


class DAQCSonar:

    def __init__(self, address: int, channel: int):
        """
        Initialize the DAQC1Sonar controller.

        Parameters
        ----------
        address : int
            The address of the DAQC1 plate.
        """
        if not isinstance(address, int):
            raise TypeError(
                "address must be an integer, not type {}".format(type(address))
            )
        if not isinstance(channel, int):
            raise TypeError(
                "channel must be an integer, not type {}".format(type(channel))
            )

        self._address = address
        self._active_channels = [False] * 7
  
    # PUBLIC METHODS
    def get_distance(self, channel: int) -> float:
        """Get the distance from the sonar sensor."""
        self._verify_active(channel)
        return DAQC.getRANGE(self._address, channel, "c")
    
    def get_distance_fast(self, channel: int) -> float:
        """Get the distance from the sonar sensor.
        
        This method skips the active check for faster performance.
        """
        return DAQC.getRANGE(self._address, channel, "c")
    
    def get_distance_all(self) -> list:
        """Get the distance from all sonar sensors."""
        return [self.get_distance_fast(i) if i else None for i in self._active_channels]
    
    def set_active(self, channel: int) -> ...:
        """Set the specified channel to active."""
        self._verify_sonar(channel)
        self._active_channels[channel - 1] = True

    def set_inactive(self, channel: int) -> ...:
        """Set the specified channel to inactive."""
        self._verify_sonar(channel)
        self._active_channels[channel - 1] = False

    # PRIVATE METHODS
    def _verify_sonar(self, channel: int) -> ...:
        """Verify the sonar is connected."""
        if not isinstance(channel, int):
            raise TypeError(
                "channel must be an integer, not type {}".format(type(channel))
            )
        if channel not in range(1, 8):
            raise ValueError("channel must be in range 1-7, not {}".format(channel))

    def _verify_active(self, channel: int) -> ...:
        """Verify the channel is active."""
        self._verify_sonar(channel)
        if not self._active_channels[channel - 1]:
            raise ValueError("channel {} is not active".format(channel))

        

