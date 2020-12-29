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
    channels = []
    time = 0.0
    params = {}
    elements = []

    def pulse(self, *args, **kwargs):

        p = Pulse(*args, **kwargs, external_params=self.params)

        if p.defer_start_time:
            p.start_time = self.time
            self.time = p.end_time()

        p.render(super())

        try:
            super().text(**p.label_params())
        except:
            pass

        try:
            super().text(**p.phase_params())
        except:
            pass

        self.elements.append(p)

    def delay(self, *args, **kwargs):

        if isinstance(args[0], Delay):

            if len(args) > 1:
                raise ValueError("No args allowed if a Delay object is supplied")

            else:
                d = Delay(args[0].args, **kwargs, external_params=self.params)

        else:
            d = Delay(*args, **kwargs, external_params=self.params)

        if d.defer_start_time:
            self.time = d.end_time()

        try:
            super().text(d.label_params())
        except:
            pass

        self.elements.append(d)

    def fid(self, *args, **kwargs):

        self.pulse(
            *args, **kwargs, shape="fid", truncate_off=True, open=True, facecolor="none"
        )

    def add_elements(self, arg):

        if isinstance(arg, str):
            psq = PulseSeq(arg, external_params=self.params)
            self.elements += psq.elements

    def reset(self):
        """
        Removes all channels and resets the time to zero

        """
        self.channels = []
        self.time = 0.0
        self.elements = []

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
