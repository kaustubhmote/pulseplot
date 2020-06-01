"""
Utilities for making plots

"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.projections import register_projection
from matplotlib.patches import Polygon
from .parse import (
    parse_multiline,
    parse_single,
    collect_phase_params,
    collect_pulse_params,
    collect_pulse_timings,
    collect_text_params,
    phasetext,
    text_wrapper
)


def pplot(*args, **kwargs):
    """
    Wrapper around matplotlib.pyplot

    """
    register_projection(PulseProgram)

    if "subplot_kw" in kwargs.keys():
        kwargs["subplot_kw"]["projection"] = "PulseProgram"
    else:
        kwargs["subplot_kw"] = {"projection": "PulseProgram"}

    fig, ax = plt.subplots(*args, **kwargs)

    return fig, ax


def shaped_pulse(start, length, shape=None, spacing=None, npoints=100):
    """
    Generates a shaped pulse in multiple ways

    """
    x = np.linspace(start + spacing, start + length - spacing, npoints)

    if shape is None:
        y = 1.0 + 0.0 * x

    elif callable(shape):
        y = shape(x)

    elif isinstance(shape, (list, tuple)):
        if len(shape) == x.shape[-1]:
            y = shape
        else:
            raise ValueError("the given shape is incompatible with the time array")

    elif isinstance(shape, np.ndarray):
        if shape.shape[-1] == x.shape[-1]:
            y = shape
        else:
            raise ValueError("the given shape is incompatible with the time array")

    return x, y


class PulseProgram(plt.Axes):
    """
    A class that defines convinience functions for
    plotting elements of a NMR pulse squence on a 
    matplotlib axes object.

    Usage
    -----
    >>> from pulseplot import pplot 
    >>> fig, ax = pplot()
    >>> ax.pulse("p1 pl1 ph1 ch1")
    >>> ax.delay(2)
    >>> ax.pulse("p2 pl1 ph2 ch1")
    >>> ax.delay(1)

    """
    name = "PulseProgram"
    channels = []
    time = 0.0
    params = {}
    spacing = 0.0

    def reset(self):
        """
        Removes all channels and resets the time to zero

        """
        self.channels = []
        self.time = 0.0

    def draw_channels(self, limits=None, color="k", **kwargs):
        """
        Draws lines marking the channels

        """
        for i in self.channels:
            if limits is None:
                super().plot([0, self.time], [i, i], color=color, **kwargs)
            else:
                super().plot(limits, [i, i], color=color, **kwargs)

    def pseq(self, instruction, **kwargs):
        """
        Main way in which 
        
        """
        seq = parse_multiline(instruction, self.params)
        
        for line in seq:
            arguments = {}
            keys = line.keys()

            if "pulse" in keys:
                arguments = {**line["pulse"], **arguments}

                if "phase" in keys:
                    arguments = {**line["phase"], **arguments}

                if "text" in keys:
                    arguments = {**line["text"], **arguments}

                arguments = {**arguments, **kwargs}
                self.pulse(**arguments)

            elif "delay" in keys:
                arguments = {**line["delay"], **arguments}
                
                if "text" in keys:
                    arguments = {**line["text"], **arguments}

                arguments = {**arguments, **kwargs}
                self.delay(**arguments)

    def pulse(
        self,
        plen=0.1,
        power=1.0,
        shape=None,
        channel=0,
        npoints=100,
        truncate=True,
        start_time=None,
        pulse_params=None,
        pulse_timing=None,
        phase_params=None,
        text_params=None,
        _type="pulse",
        **kwargs,
    ):
        """
        Adds a pulse to the plot

        """
        assert _type == "pulse"

        # collect parameters in appropriate dictionaries
        pulse_timing, kwargs = collect_pulse_timings(pulse_timing, kwargs)
        phase_params, kwargs = collect_phase_params(phase_params, kwargs)
        text_params, kwargs = collect_text_params(text_params, kwargs)
        pulse_params, kwargs = collect_pulse_params(pulse_params, kwargs, truncate=truncate)

        # pass all remaining parameters to pulse paramaters
        pulse_params = {**pulse_params, **kwargs}

        if channel not in self.channels:
            self.channels.append(channel)

        if start_time is None:
            t0 = self.time
        else:
            t0 = start_time

        if pulse_timing["centered"]:
            t0 -= plen / 2
            if pulse_timing["keep_centered"]:
                t1 = t0
            else:
                t1 = t0 + plen / 2
        else:
            if pulse_timing["wait"]:
                t1 = t0
            else:
                t1 = t0 + plen

        self.time = t1

        xscale, shape = shaped_pulse(
            start=t0, length=plen, shape=shape, spacing=self.spacing, npoints=npoints,
        )

        shape *= power

        if not truncate:
            super().plot(xscale, shape + channel, **kwargs)

        else:
            vertices = [[xscale[0], channel]]
            for v in [[i, j + channel] for i, j in zip(xscale, shape)]:
                vertices.append(v)
            vertices.append([xscale[-1], channel])

            pulse_patch = Polygon(vertices, **pulse_params,)
            super().add_patch(pulse_patch)

        if phase_params["phase"] is not None:
            x = t0 + plen / 2 
            y = shape[len(shape) // 2] + channel + 0.2
            phase_params["x"] = x
            phase_params["y"] = y
            phase_params["phase"] = phasetext(phase_params["phase"])
            phase_params = text_wrapper(**phase_params)
            super().text(**phase_params)

        if text_params["text"] is not None:
            x = t0 + plen / 2 
            y = shape[len(shape) // 2] / 2 + channel 
            text_params["x"] = x
            text_params["y"] = y
            text_params.pop("channel")
            text_params = text_wrapper(**text_params)
            super().text(**text_params)


    def delay(self, time, _type="delay", text_params=None, **kwargs):
        """
        Adds a delay to the axes

        """
        assert _type == "delay"

        text_params, kwargs = collect_text_params(text_params, kwargs)

        if text_params["text"] is not None:
            x = self.time + time / 2 
            y = text_params["channel"] + 0.1 
            text_params.pop("channel")
            text_params["x"] = x
            text_params["y"] = y
            text_params = text_wrapper(**text_params)
            super().text(**text_params, **kwargs)

        self.time += time

    def fid(self, time, channel, amp=0.2, shift=0, frequency=20, decay=1, **kwargs):

        self.pulse(
            plen=time,
            power=1,
            channel=channel,
            shape=lambda x: amp * np.exp(1j * frequency * x - decay * x).real + shift,
            truncate=False,
            **kwargs,
        )
