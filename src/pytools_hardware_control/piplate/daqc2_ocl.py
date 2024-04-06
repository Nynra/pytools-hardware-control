import piplates.DAQC2plate as DAQC2
from typing import Union
from threading import Thread, Event


class Oscilloscope:
    """Class for controlling the Pi-Plate DAQC2 oscilloscope

    The Pi-Plate DAQC2 oscilloscope has two channels, each with a 10-bit ADC.
    The oscilloscope can be controlled to sweep at different rates, trigger on
    different sources, and trigger at different levels. The oscilloscope can
    also be set to trigger on either rising or falling edges.

    Specifications
    ^^^^^^^^^^^^^^^
    - Input voltage range: 0-12V
    - Input bandwidth: 370Khz
    - Input impedance: 1MΩ
    - Max samplerate one channel: 1Mhz
    - Max samplerate two channels: 500Khz
    - Trace buffer size: 1024 samples
    - Resolution: 12 bits
    - Trigger jitter: 2us max

    .. attention::

        When using this class make sure that ADC pin 1 and 2 on the DAQC2 are free
        and the DAQC2 plate is not in function generator mode. This is not checked
        by this class.
    """
    _trigger_range = (0, 4095)  # Trigger range in mV
    _trigger_voltage_scale_factor = 12/4095  # 12V / 4095mV

    def __init__(self, address: int = 0) -> ...:
        """Initialize the PiPlateScope object

        To use this class ADC pin 0 and 4 on the DAQC2 must be free and
        the DAQC2 plate must not be in function generator (FG) mode.

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
        self._sweep_rate = 9
        self._trig_source = 1
        self._trig_level = 0.00
        self._trig_type = 0  # 0 for auto, 1 for edge
        self._trig_edge = 0  # 0 for rising, 1 for falling
        self._triggered = False
        self._channel_one_active = False
        self._channel_two_active = False

        # Placeholders used during sweeping
        self._channel_one_trace = DAQC2.trace1
        self._channel_two_trace = DAQC2.trace2
        self._sweep_thread = None
        self._stop_event = Event()

    # DUNDER METHODS
    def __repr__(self) -> str:
        return f"PiPlateScope(address={self._address})"

    def __str__(self) -> str:
        return f"PiPlateScope at address {self._address}"

    def __del__(self) -> ...:
        self.disable()

    # PROPERTIES
    @property
    def sweep_rate(self) -> int:
        """Get or set the sweep rate of the oscilloscope

        The sweep rate is the time between each sweep of the oscilloscope.
        The sweep rate can be set to any of the following values:
        - 0: 100hz = 10ms
        - 1: 200hz = 5ms
        - 2: 500hz = 2ms
        - 3: 1khz = 1ms
        - 4: 2khz = 500us
        - 5: 5khz = 200us
        - 6: 10khz = 100us
        - 7: 20khz = 50us
        - 8: 50khz = 20us
        - 9: 100khz = 10us
        - 10: 200khz = 5us
        - 11: 500khz = 2us
        - 12: 1mhz = 1us

        Where 12 is only allowed with one channel active.

        Parameters
        ----------
        rate : int
            The sweep rate to set

        Returns
        -------
        int
            The current sweep rate
        """
        return self._sweep_rate

    @sweep_rate.setter
    def sweep_rate(self, rate: int) -> ...:
        if not isinstance(rate, int):
            raise TypeError(f"Invalid sweep rate type: {type(rate)}")
        if rate not in range(13):
            raise ValueError(f"Invalid sweep rate: {rate}")
        if rate == 12 and self.channel_two_active:
            raise ValueError("Sweep rate 12 is only allowed with one channel active")
        self._sweep_rate = rate
        self._reset_sweep_rate()

    @property
    def channel_one_active(self) -> bool:
        """Get or set whether channel one is active

        Parameters
        ----------
        active : bool
            Whether channel one should be active

        Returns
        -------
        bool
            Whether channel one is active
        """
        return self._channel_one_active

    @channel_one_active.setter
    def channel_one_active(self, active: bool) -> ...:
        if not isinstance(active, bool):
            raise TypeError(f"Invalid channel one active type: {type(active)}")
        self._channel_one_active = active
        self._reset_channels()
        
    @property
    def channel_two_active(self) -> bool:
        """Get or set whether channel two is active

        Parameters
        ----------
        active : bool
            Whether channel two should be active

        Returns
        -------
        bool
            Whether channel two is active
        """
        return self._channel_two_active

    @channel_two_active.setter
    def channel_two_active(self, active: bool) -> ...:
        if not isinstance(active, bool):
            raise TypeError(f"Invalid channel two active type: {type(active)}")
        self._channel_two_active = active
        self._reset_channels()

    @property
    def trigger_source(self) -> int:
        """Get or set the trigger source

        The trigger source can be set to either channel one or channel two.

        Parameters
        ----------
        source : int
            The trigger source to set

        Returns
        -------
        int
            The current trigger source"""
        return self._trig_source

    @trigger_source.setter
    def trigger_source(self, source: int) -> ...:
        if not isinstance(source, int):
            raise TypeError(f"Invalid trigger source type: {type(source)}")
        if source not in (1, 2):
            raise ValueError(f"Invalid trigger source: {source}")
        self._trig_source = source
        self._reset_trigger()

    @property
    def trigger_level(self) -> float:
        """Get or set the trigger level

        The trigger level is the voltage level at which the oscilloscope will
        trigger. The trigger level can be set to any value between 0 and 4095 mV.

        Parameters
        ----------
        level : float
            The trigger level to set

        Returns
        -------
        float
            The current trigger level
        """
        return self._trig_level

    @trigger_level.setter
    def trigger_level(self, level: float) -> ...:
        if not isinstance(level, (int, float)):
            raise TypeError(f"Invalid trigger level type: {type(level)}")
        if level not in range(*self._trigger_range):
            raise ValueError(f"Invalid trigger level: {level}")
        self._trig_level = level
        self._reset_trigger()


    @property
    def trigger_type(self) -> int:
        """Get or set the trigger type

        The trigger type can be set to either auto or edge. Auto will trigger
        the oscilloscope automatically, while edge will trigger the oscilloscope
        on a rising or falling edge.

        Parameters
        ----------
        trig_type : int
            The trigger type to set

        Returns
        -------
        int
            The current trigger type
        """
        return self._trig_type

    @trigger_type.setter
    def trigger_type(self, trig_type: int) -> ...:
        if not isinstance(trig_type, int):
            raise TypeError(f"Invalid trigger type: {type(trig_type)}")
        if trig_type not in (0, 1):
            raise ValueError(f"Invalid trigger type: {trig_type}")
        self._trig_type = trig_type

    @property
    def trigger_edge(self) -> int:
        """Get or set the trigger edge

        The trigger edge can be set to either rising or falling. The oscilloscope
        will trigger on the specified edge when the trigger type is set to edge.

        Parameters
        ----------
        edge : int
            The trigger edge to set

        Returns
        -------
        int
            The current trigger edge
        """
        return self._trig_edge

    @trigger_edge.setter
    def trigger_edge(self, edge: int) -> ...:
        if not isinstance(edge, int):
            raise TypeError(f"Invalid trigger edge type: {type(edge)}")
        if edge not in (0, 1):
            raise ValueError(f"Invalid trigger edge: {edge}")
        self._trig_edge = edge

    @property
    def channel_one_trace(self) -> int:
        """Get the current trace of channel one"""
        return self._channel_one_trace
    
    @property
    def trace1(self) -> int:
        """Get the current trace of channel one"""
        return self._channel_one_trace

    @property
    def channel_two_trace(self) -> int:
        """Get the current trace of channel two"""
        return self._channel_two_trace
    
    @property
    def trace2(self) -> int:
        """Get the current trace of channel two"""
        return self._channel_two_trace

    # PUBLIC FUNCTIONS
    def enable(self) -> ...:
        """Start sweeping the oscilloscope with the current settings"""
        DAQC2.startOSC(self._address)
        self._reset_channels()
        self._reset_trigger()
        self._reset_sweep_rate()
        self._sweep_thread = Thread(target=self._sweep, args=(self._stop_event,))
        self._sweep_thread.start()

    def disable(self) -> ...:
        """Stop sweeping the oscilloscope"""
        self._stop_event.set()
        self._sweep_thread.join()
        self._stop_event.clear()
        DAQC2.stopOSC(self._address)

    # PRIVATE FUNCTIONS
    def _sweep(self, stop_event: Event) -> ...:
        """Sweep the active channels.

        Keeps sweeping the oscilloscope until the stop event is set.
        """
        DAQC2.intEnabled(self._address)
        DAQC2.runOSC(self._address)
        while not stop_event.is_set():
            data_ready = 0
            while not data_ready and not stop_event.is_set():
                if DAQC2.GPIO.input(22)==0:
                    data_ready = 1
                    DAQC2.getINTflags(self._address)
            DAQC2.getOSCtraces(self._address)

    def _reset_trigger(self) -> ...:
        DAQC2.setOSCtrigger(
            addr=self._address,
            channel=self._trig_source,
            type=self._trig_type,
            edge=self._trig_edge,
            level=self._trig_level,
        )

    def _reset_channels(self) -> ...:
        DAQC2.setOSCchannel(
            self._address,
            int(self._channel_one_active),
            int(self._channel_two_active)
        )

    def _reset_sweep_rate(self) -> ...:
        DAQC2.setOSCsweep(self._address, self._sweep_rate)