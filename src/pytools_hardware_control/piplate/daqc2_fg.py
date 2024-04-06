import piplates.DAQC2plate as DAQC2
from typing import Union


class FunctionGenerator:
    """Class for controlling the Pi-Plate DAQC2 function generator

    The Pi-Plate DAQC2 function generator can generate a sine wave, square wave,
    or triangle wave. The function generator can also be set to a specific
    frequency and amplitude.

    .. attention::

        Make sure DAC 0 and 1 are not in use and the DAQC plate is not in
        osciloscope mode before using the function generator. This is not
        checked by this class
    """

    _frequency_range = (10, 10000)  # Frequency range in Hz
    _waveforms = [
        "sine",
        "triangle",
        "square",
        "sawtooth rising",
        "sawtooth falling",
        "noise",
        "sinc",
    ]

    def __init__(self, address: int = 0) -> ...:
        """Initialize the PiPlateFunctionGenerator object

        To use this class DAC 0 and 1 on the DAQC2 must be free and the DAQC2
        plate must not be in oscilloscope mode.

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
        self._waveform = [0, 0]
        self._frequency = [1000, 1000]
        self._amplitude = [1, 1]

    # DUNDER METHODS
    def __repr__(self) -> str:
        return f"PiPlateFunctionGenerator(address={self._address})"

    def __str__(self) -> str:
        return f"PiPlateFunctionGenerator at address {self._address}"

    # PUBLIC FUNCTIONS
    def enable(self) -> ...:
        """Enable the function generator.
        
        This will force the DAQC2 plate in to FG mode.
        """
        DAQC2.fgON(self._address)

    def disable(self) -> ...:
        """Disable the function generator
        
        Both channels need to be disabled to release the DAQC2 plate from FG mode.
        """
        DAQC2.fgOFF(self._address)

    def set_waveform(self, channel: int, waveform: Union[str, int]) -> ...:
        """Set the waveform of the function generator

        Parameters
        ----------
        channel : int
            The channel to set the waveform for. Possible values are:
            - 0: DAC 0
            - 1: DAC 1
        waveform : str
            The waveform to set. Possible values are:
            - 0: 'sine'
            - 1: 'triangle'
            - 2: 'square'
            - 3: 'sawtooth rising'
            - 4: 'sawtooth falling'
            - 5: 'noise'
            - 6: 'sinc'
        """
        if isinstance(waveform, int):
            if waveform < 0 or waveform >= len(self._waveforms):
                raise ValueError(f"Invalid waveform: {waveform}")
        elif isinstance(waveform, str):
            if waveform.lower() not in self._waveforms:
                raise ValueError(f"Invalid waveform: {waveform}")
            waveform = self._waveforms.index(waveform.lower())
        else:
            raise TypeError(f"Invalid waveform type: {type(waveform)}")

        self._waveform[channel] = waveform
        DAQC2.fgTYPE(self._address, waveform)

    def get_waveform(self, channel: int) -> int:
        """Get the waveform of the function generator

        Parameters
        ----------
        channel : int
            The channel to get the waveform for. Possible values are:
            - 0: DAC 0
            - 1: DAC 1

        Returns
        -------
        int
            The current waveform
        """
        if channel < 0 or channel >= len(self._waveform):
            raise ValueError(f"Invalid channel: {channel}")
        return self._waveform[channel]

    def set_frequency(self, channel: int, frequency: int) -> ...:
        """Set the frequency of the function generator

        Parameters
        ----------
        channel : int
            The channel to set the frequency for. Possible values are:
            - 0: DAC 0
            - 1: DAC 1
        frequency : int
            The frequency to set in Hz
        """
        if not isinstance(frequency, int):
            raise TypeError(f"Invalid frequency type: {type(frequency)}")
        if not (self._frequency_range[0] <= frequency <= self._frequency_range[1]):
            raise ValueError(f"Invalid frequency: {frequency}")

        self._frequency[channel] = frequency
        DAQC2.fgFREQ(self._address, channel, frequency)

    def get_frequency(self, channel: int) -> int:
        """Get the frequency of the function generator

        Parameters
        ----------
        channel : int
            The channel to get the frequency for. Possible values are:
            - 0: DAC 0
            - 1: DAC 1

        Returns
        -------
        int
            The current frequency
        """
        if channel < 0 or channel >= len(self._frequency):
            raise ValueError(f"Invalid channel: {channel}")
        return self._frequency[channel]

    def set_attenuation(self, channel: int, attenuation: Union[str, int]) -> ...:
        """Set the attenuation of the function generator

        Parameters
        ----------
        channel : int
            The channel to set the attenuation for. Possible values are:
            - 0: DAC 0
            - 1: DAC 1
        attenuation : str
            The attenuation to set. Possible values are:
            - 1: 1      = 0 - 5V
            - 2: 1/2    = 0 - 2.5V
            - 3: 1/4    = 0 - 1.25V
            - 4: 1/8    = 0 - 0.625V
        """
        if isinstance(attenuation, int):
            if attenuation < 1 or attenuation > 4:
                raise ValueError(f"Invalid attenuation: {attenuation}")
        elif isinstance(attenuation, str):
            if attenuation not in ["1", "1/2", "1/4", "1/8"]:
                raise ValueError(f"Invalid attenuation: {attenuation}")
            attenuation = ["1", "1/2", "1/4", "1/8"].index(attenuation) + 1
        else:
            raise TypeError(f"Invalid attenuation type: {type(attenuation)}")

        DAQC2.fgAMPL(self._address, channel, attenuation)
        self._amplitude[channel] = attenuation

    def get_attenuation(self, channel: int) -> int:
        """Get the attenuation of the function generator

        Parameters
        ----------
        channel : int
            The channel to get the attenuation for. Possible values are:
            - 0: DAC 0
            - 1: DAC 1

        Returns
        -------
        int
            The current attenuation
        """
        if channel < 0 or channel >= len(self._amplitude):
            raise ValueError(f"Invalid channel: {channel}")
        return self._amplitude[channel]


