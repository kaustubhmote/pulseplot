"""
Utilities for making plots

"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.projections import register_projection
from .parse import PulseSeq, Pulse, Delay


def pplot(*args, **kwargs):
    """
    Wrapper around matplotlib.pyplot
    Automatically incorporates the PulseProgram projection
    in subplot keywords

    """
    register_projection(PulseProgram)

    if "subplot_kw" in kwargs.keys():
        kwargs["subplot_kw"]["projection"] = "PulseProgram"
    else:
        kwargs["subplot_kw"] = {"projection": "PulseProgram"}

    fig, ax = plt.subplots(*args, **kwargs)

    return fig, ax


class PulseProgram(plt.Axes):
    """
    A class that defines convinience functions for
    plotting elements of a NMR pulse squence on a 
    matplotlib axes object.

    Usage
    -----
    >>> from pulseplot import pplot 
    >>> fig, ax = pplot()
    >>> ax.params["p1"] = 0.5
    >>> ax.pulse("p1 pl1 ph1 f1")
    >>> ax.delay(2)
    >>> ax.pulse("p2 pl1 ph2 f1 w")
    >>> ax.pulse("p2 pl1 ph2 f2")
    >>> ax.delay(2)
    >>> ax.pulse("p1 pl1 ph2 f1 w")
    >>> ax.pulse("p1 pl1 ph2 f2 w")
    >>> ax.fid("p1 pl1 phrec f2")

    """

    name = "PulseProgram"

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.spacing = 0.0
        self.phase_dy = 0.0
        self.text_dy = 0.0
        self.fontsize = None
        self.time = 0.0
        self.params = {}
        self.limits = {"xlow": 0.9, "xhigh": 2, "ylow": -0.1, "yhigh": 2}
        self.set_limits()

    def pulse(self, *args, **kwargs):

        if isinstance(args[0], Pulse):
            p = args[0]

        else:
            p = Pulse(*args, **kwargs, external_params=self.params)

        if p.defer_start_time:
            p.start_time = self.time
            p.start_time += self.spacing
            p.plen -= self.spacing
            self.time = p.end_time()

        p.text_dy += self.text_dy
        p.phtxt_dy += self.phase_dy

        if self.fontsize:
            if "fontsize" not in p.text_kw:
                p.text_kw["fontsize"] = self.fontsize
            if "fontsize" not in p.phase_kw:
                p.phase_kw["fontsize"] = self.fontsize

        # add the actual pulse
        pulse_patch = p.patch()
        super().add_patch(pulse_patch)

        xarr, yarr = pulse_patch.xy[:, 0], pulse_patch.xy[:, 1]
        self.edit_limits(
            xlow=min(xarr), xhigh=max(xarr), ylow=min(yarr), yhigh=max(yarr)
        )

        p.start_time -= self.spacing
        p.plen += self.spacing

        try:
            super().text(**p.label_params())
            xpos, ypos = p.label_params["x"], p.label_params["y"]
            self.edit_limits(xlow=xpos, xhigh=xpos, ylow=ypos, yhigh=ypos)
        except:
            pass

        try:
            super().text(**p.phase_params())
            xpos, ypos = p.phase_params["x"], p.phase_params["y"]
            self.edit_limits(xlow=xpos, xhigh=xpos, ylow=ypos, yhigh=ypos)
        except:
            pass

        p.text_dy -= self.text_dy
        p.phtxt_dy -= self.phase_dy

    def delay(self, *args, **kwargs):

        if isinstance(args[0], Delay):
            d = args[0]

        else:
            d = Delay(*args, **kwargs, external_params=self.params)

        if d.defer_start_time:
            d.start_time = self.time

        self.time += d.time

        try:
            super().text(**d.label_params())
        except:
            pass

    def fid(self, *args, **kwargs):

        self.pulse(
            *args,
            **kwargs,
            shape="fid",
            truncate_off=True,
            open=True,
            facecolor="none",
        )

    def clear(self):
        """
        Removes all channels and resets the time to zero

        """
        self.time = 0.0
        super().clear()

    def draw_channels(self, limits=None, color="k", **kwargs):
        """
        Draws lines marking the channels

        """
        for i in self.channels:
            if limits is None:
                super().plot([0, self.time], [i, i], color=color, **kwargs)
            else:
                super().plot(limits, [i, i], color=color, **kwargs)

    def pseq(self, instruction):
        """
        Main way in which 
        
        """
        if isinstance(instruction, str):
            instruction = PulseSeq(instruction, external_params=self.params)

        for item in instruction.elements:
            if isinstance(item, Pulse):
                self.pulse(item)
            elif isinstance(item, Delay):
                self.delay(item)

    def set_limits(self, limits=None):

        if limits is not None:
            self.limits = limits

        try:
            super().set_xlim(self.limits["xlow"], self.limits["xhigh"])
            super().set_ylim(self.limits["ylow"], self.limits["yhigh"])
        except IndexError:
            raise IndexError("limits should be given as [xlow, xhigh, ylow, yhigh]")

    def edit_limits(self, xlow=None, xhigh=None, ylow=None, yhigh=None):

        if (xlow is not None) and (xlow - 0.5 < self.limits["xlow"]):
            self.limits["xlow"] = xlow - 0.5

        if (ylow is not None) and (ylow - 0.5 < self.limits["ylow"]):
            self.limits["ylow"] = ylow - 0.5

        if (xhigh is not None) and (xhigh + 0.5 > self.limits["xhigh"]):
            self.limits["xhigh"] = xhigh + 0.5

        if (yhigh is not None) and (yhigh + 0.5 > self.limits["yhigh"]):
            self.limits["yhigh"] = yhigh + 0.5

        self.set_limits()

