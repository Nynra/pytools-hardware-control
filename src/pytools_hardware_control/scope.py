"""Tektronix scope driver

This module provides a driver for the Tektronix scope. Most of the code in this repository is based on the code from the Tektronix scope driver.
Most modifications either add documentation or student friendly functions.
"""

from time import *
import numbers
import numpy as np
import pyvisa as visa
from builtins import str as unicode
from typing import Union
from .exceptions import TektronixScopeError


class TektronixScope(object):
    """Drive a TektronixScope instrument"""

    def __init__(self, inst: str) -> ...:
        """Initialise the Scope

        Parameters
        ----------
        inst : str
            should be a string or an object with write and ask method
        """
        if not hasattr(inst, "write"):
            if isinstance(inst, str):
                if visa is not None:
                    rm = visa.ResourceManager()
                    inst = rm.open_resource(inst)
                else:
                    raise Exception("Visa is not install on your system")
            else:
                raise ValueError("First argument should be a string or an instrument")
        self._inst = inst

    def _write(self, cmd: str):
        return self._inst.write(cmd)

    def ask(self, cmd: str):
        return self._inst.ask(cmd)

    def ask_raw(self, cmd: str):
        if hasattr(self._inst, "ask_raw"):
            return self._inst.ask_raw(cmd)[:-1]
        else:
            return self._inst.ask(cmd)

    # Acquisition Command Group
    def start_acq(self) -> ...:
        """Start acquisition"""
        self._write("ACQ:STATE RUN")

    def stop_acq(self) -> ...:
        """Stop acquisition"""
        self._write("ACQ:STATE STOP")

    # Horizontal Command Group
    def get_horizontal_scale(self) -> float:
        """Return the horizontal scale in second/division"""
        return float(self.ask("HORizontal:SCAle?"))

    def set_horizontal_scale(self, val: float):
        """Set the horizontal scale in second/division"""
        if not isinstance(val, numbers.Number):
            raise TektronixScopeError(
                "Horizontal scale should be a number not {}".format(val)
            )
        return self._write("HORizontal:SCAle {val}".format(val=val))

    # Miscellaneous Command Group
    def _load_setup(self):
        l = self.ask("SET?")
        dico = dict([e.split(" ", 1) for e in l.split(";")[1:]])
        self.dico = dico

    def get_setup_dict(self, force_load: bool = False) -> dict:
        """Return the dictionnary of the setup

        By default, the method does not load the setup from the instrument
        unless it has not been loaded before or force_load is set to true.
        """
        if not hasattr(self, "dico") or force_load:
            self._load_setup()
        return self.dico

    def number_of_channel(self) -> int:
        """Return the number of available channel on the scope (4 or 2)"""
        if ":CH4:SCA" in self.get_setup_dict().keys():
            return 4
        else:
            return 2

    # Vertical Command Group
    def channel_name(self, name: Union[str, int]) -> str:
        """Return and check the channel name

        Return the channel CHi from either a number i, or a string 'i', 'CHi'

        Parameters
        ----------
        name : str or int
            name or number of the channel

        Returns
        -------
        str
            name of the channel

        Raises
        ------
        TektronixScopeError
            If the channel name is not valid
        """
        n_max = self.number_of_channel()
        channel_list = ["CH%i" % (i + 1) for i in range(n_max)]
        channel_listb = ["%i" % (i + 1) for i in range(n_max)]
        if isinstance(name, numbers.Number):
            if name > n_max:
                raise TektronixScopeError(
                    "Request channel %i while channel number should be between %i and %i"
                    % (name, 1, n_max)
                )
            return "CH%i" % name
        elif name in channel_list:
            return name
        elif name in channel_listb:
            return "CH" + name
        else:
            raise TektronixScopeError(
                "Request channel %s while channel should be in %s"
                % (str(name), " ".join(channel_list))
            )

    def is_channel_selected(self, channel: Union[int, str]) -> bool:
        """Return true if the channel is selected"""
        channel = self.channel_name(channel)
        return self.ask("SEL:%s?" % (self.channel_name(channel))) == "1"

    def get_channel_offset(self, channel: Union[int, str]) -> float:
        """Returns the vertical offset of the channel"""
        channel = self.channel_name(channel)
        return float(self.ask("%s:OFFS?" % self.channel_name(channel)))

    def get_channel_position(self, channel: Union[int, str]) -> float:
        """Returns the vertical position of the channel"""
        channel = self.channel_name(channel)
        return float(self.ask("%s:POS?" % self.channel_name(channel)))

    def get_vertical_scale(self, channel: Union[int, str]) -> float:
        """Returns the vertical scale of the channel"""
        channel = self.channel_name(channel)
        return float(self.ask("%s:SCA?" % self.channel_name(channel)))

    def set_impedance(self, channel: Union[int, str], value: str) -> ...:
        """
        Sets the input impedance of the channel

        Parameters
        ----------
        channel : str
            name of the channel
        value : str
            value of the impedance
        """
        channel = self.channel_name(channel)
        liste_string = [
            "FIF",
            "FIFty",
            "SEVENTYF",
            "SEVENTYFive",
            "MEG",
            "50",
            "75",
            "1.00E+06",
        ]
        liste_value = [50, 75, 1.00e6]
        if isinstance(value, str) or isinstance(value, unicode):
            if value.lower() not in map(lambda a: a.lower(), liste_string):
                raise TektronixScopeError(
                    "Impedance is %s. It should be in %s" % liste_string
                )
        elif isinstance(value, numbers.Number):
            if value not in liste_value:
                raise TektronixScopeError(
                    "Impedance is %s. It should be in %s" % liste_value
                )
            else:
                value = str(value) if value < 100 else "1.00E+06"
        else:
            raise TektronixScopeError(
                "Impedance is %s. It should be in %s" % liste_string
            )
        self.write("%s:IMPedance %s" % (self.channel_name(channel), value))

    def get_impedance(self, channel: Union[int, str]) -> str:
        """Returns the input impedance of the channel"""
        channel = self.channel_name(channel)
        return self.ask("%s:IMPedance?" % self.channel_name(channel))

    def set_coupling(self, channel: Union[int, str], value: str):
        """Sets the input coupling of the channel"""
        channel = self.channel_name(channel)
        liste_string = ["AC", "DC", "GND"]
        if isinstance(value, str) or isinstance(value, unicode):
            if value.lower() not in map(lambda a: a.lower(), liste_string):
                raise TektronixScopeError(
                    "Coupling is %s. It should be in %s" % liste_string
                )
        else:
            raise TektronixScopeError(
                "Coupling is %s. It should be in %s" % liste_string
            )
        self.write("%s:COUPling %s" % (self.channel_name(channel), value))

    def get_coupling(self, channel: Union[int, str]) -> str:
        """Returns the input coupling of the channel"""
        channel = self.channel_name(channel)
        return self.ask("%s:COUPling?" % self.channel_name(channel))

    # Waveform Transfer Command Group
    def set_data_source(self, name):
        """Set the data source of the waveform record"""
        name = self.channel_name(name)
        self.write("DAT:SOUR " + str(name))

    def set_data_start(self, data_start: int) -> ...:
        """
        Set the first data points of the waveform record.

        If data_start is None: data_start=1. The waveform record range
        is the the horizontal record length on the osciloscope. The range
        that will be measured and exported is set by the data_start and
        data_stop parameters.
        """
        if not isinstance(data_start, (int, None)):
            raise TektronixScopeError(
                "data_start should be a number not {}".format(data_start)
            )
        if data_start is None:
            data_start = 1
        self.write("DATA:START %i" % data_start)

    def get_data_start(self) -> int:
        """Return the first data points of the waveform record."""
        return int(self.ask("DATA:START?"))

    def get_horizontal_record_length(self) -> int:
        """
        Return the horizontal record length

        The horzontal record length is the number of points in the waveform
        record.
        """
        return int(self.ask("horizontal:recordlength?"))

    def set_horizontal_record_length(self, val: Union[int, str]) -> ...:
        """Set the horizontal record length"""
        if not isinstance(val, numbers.Number):
            raise TektronixScopeError(
                "horizontal record length should be a number not {}".format(val)
            )
        self.write("HORizontal:RECOrdlength %s" % str(val))

    def set_data_stop(self, data_stop: Union[int, str, None] = None) -> ...:
        """
        Set the last data points of the waveform record

        If data_stop is None: data_stop= horizontal record length
        """
        if data_stop is None:
            data_stop = self.get_horizontal_record_length()
        self.write("DATA:STOP %i" % data_stop)

    def get_data_stop(self) -> ...:
        return int(self.ask("DATA:STOP?"))

    def get_out_waveform_horizontal_sampling_interval(self) -> float:
        return float(self.ask("WFMO:XIN?"))

    def get_out_waveform_horizontal_zero(self) -> float:
        return float(self.ask("WFMO:XZERO?"))

    def get_out_waveform_vertical_scale_factor(self) -> float:
        return float(self.ask("WFMO:YMUlt?"))

    def get_out_waveform_vertical_position(self) -> float:
        return float(self.ask("WFMO:YOFf?"))

    def read_data_one_channel(
        self,
        channel: Union[int, str, None] = None,
        data_start: Union[int, None] = None,
        data_stop: Union[int, None] = None,
        x_axis_out: bool = False,
        t0: Union[int, float, None] = None,
        DeltaT: Union[int, float, None] = None,
        booster: bool = False,
    ):
        """Read waveform from the specified channel

        Parameters
        ----------
        channel : int or str or None
            name of the channel (i, 'i', 'chi'). If None, keep
            the previous channel
        data_start : int or None
            position of the first point in the waveform
        data_stop : int or None
            position of the last point in the waveform
        x_axis_out : bool
            if true, the function returns (X,Y) if false, the function returns Y (default)
        t0 : int or float or None
            initial position time in the waveform
        DeltaT : int, float or None
            duration of the acquired waveform t0, DeltaT and data_start,
            data_stop are mutually exculsive
        booster : bool
            if set to True, accelerate the acquisition by assuming
            that all the parameters are not change from the previous
            acquisition. If parameters were changed, then the output may
            be different than what is expected. The channel is the only
            parameter that is checked when booster is enable

        """
        # set booster to false if it the fist time the method is called
        # We could decide to automaticaly see if parameters of the method
        # are change to set booster to false. However, one cannot
        # detect if the setting of the scope are change
        # To be safe, booster is set to False by default.
        if booster:
            if not hasattr(self, "first_read"):
                booster = False
            else:
                if self.first_read:
                    booster = False
        self.first_read = False
        if not booster:
            # Set data_start and data_stop according to parameters
            if t0 is not None or DeltaT is not None:
                if data_stop is None and data_start is None:
                    x_0 = self.get_out_waveform_horizontal_zero()
                    delta_x = self.get_out_waveform_horizontal_sampling_interval()
                    data_start = int((t0 - x_0) / delta_x) + 1
                    data_stop = int((t0 + DeltaT - x_0) / delta_x)
                else:  # data_stop is not None or data_start is not None
                    raise TektronixScopeError(
                        "Error in read_data_one_channel,\
t0, DeltaT and data_start, data_stop args are mutually exculsive"
                    )
            if data_start is not None:
                self.set_data_start(data_start)
            if data_stop is not None:
                self.set_data_stop(data_stop)
            self.data_start = self.get_data_start()
            self.data_stop = self.get_data_stop()
        # Set the channel
        if channel is not None:
            self.set_data_source(channel)
        if not booster:
            if not self.is_channel_selected(channel):
                raise TektronixScopeError(
                    "Try to read channel %s which \
is not selectecd"
                    % (str(channel))
                )
        if not booster:
            self.write("DATA:ENCDG RIB")
            self.write("WFMO:BYTE_NR 2")
            self.offset = self.get_out_waveform_vertical_position()
            self.scale = self.get_out_waveform_vertical_scale_factor()
            self.x_0 = self.get_out_waveform_horizontal_zero()
            self.delta_x = self.get_out_waveform_horizontal_sampling_interval()

        X_axis = (
            self.x_0 + np.arange(self.data_start - 1, self.data_stop) * self.delta_x
        )

        buffer = self.ask_raw("CURVE?")
        res = np.frombuffer(
            buffer, dtype=np.dtype("int16").newbyteorder(">"), offset=int(buffer[1]) + 2
        )
        # The output of CURVE? is scaled to the display of the scope
        # The following converts the data to the right scale
        Y = (res - self.offset) * self.scale
        if x_axis_out:
            return X_axis, Y
        else:
            return Y
