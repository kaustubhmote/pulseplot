"""
Utilities for making plots

"""
from warnings import warn
import matplotlib.pyplot as plt
from matplotlib.projections import register_projection
from matplotlib.animation import ArtistAnimation

from .parse import Delay, Pulse, PulseSeq


def subplots(*args, **kwargs):
    """
    Wrapper around matplotlib.pyplot.subplots
    Automatically incorporates the PulseProgram projection
    in subplot keywords

    """
    register_projection(PulseProgram)

    if "subplot_kw" in kwargs.keys():

        if "projection" in kwargs["subplot_kw"]:
            warn(
                f"Projection will be set to 'PulseProgram' instead of {kwargs['subplot_kw']['projection']}"
            )

        kwargs["subplot_kw"]["projection"] = "PulseProgram"

    else:
        kwargs["subplot_kw"] = {"projection": "PulseProgram"}

    fig, ax = plt.subplots(*args, **kwargs)

    return fig, ax


def subplot_mosaic(*args, **kwargs):
    """
    Wrapper around matplotlib.pyplot.subplot_mosiac
    Automatically incorporates the PulseProgram projection
    in subplot keywords

    """
    register_projection(PulseProgram)

    if "subplot_kw" in kwargs.keys():

        if "projection" in kwargs["subplot_kw"]:
            warn(
                f"Projection will be set to 'PulseProgram' instead of {kwargs['subplot_kw']['projection']}"
            )

        kwargs["subplot_kw"]["projection"] = "PulseProgram"

    else:
        kwargs["subplot_kw"] = {"projection": "PulseProgram"}

    fig, ax = plt.subplot_mosaic(*args, **kwargs)

    return fig, ax


def show(*args, **kwargs):
    """
    Calls matplotlib.pyplot.show
    This is just to avoid the import
    of matploltib.pyplot while making
    pulse diagrams.

    """
    plt.show(*args, **kwargs)

    return


def animation(*args, **kwargs):
    """
    Artist animation wrapper to avoid another import
    
    """

    return ArtistAnimation(*args, **kwargs)


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

        self.center_align = False
        self.spacing = 0.0
        self.phase_dy = 0.0
        self.text_dy = 0.0
        self.fontsize = None
        self.time = 0.0
        self.params = {}
        self.limits = {
            "xlow": 10,
            "xhigh": -10,
            "ylow": 10,
            "yhigh": -10,
            "dx": 0.1,
            "dy": 0.1,
        }

        self.set_limits()
        self.axis(False)

    def pulse(self, *args, **kwargs):

        if isinstance(args[0], Pulse):
            p = args[0]

        else:
            p = Pulse(*args, **kwargs, external_params=self.params)

        if p.defer_start_time:
            p.start_time = self.time + self.spacing
            p.plen -= 2 * self.spacing
            if not p.wait:
                self.time = p.end_time() + 2 * self.spacing

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

        if self.center_align:
            center = (yarr.min() + yarr.max()) / 2.0 - yarr.min()
            yarr -= center
            pulse_patch.xy[:, 1] = yarr

            p.text_dy -= center
            p.phtxt_dy -= center

        self.edit_limits(
            xlow=xarr.min(), xhigh=xarr.max(), ylow=yarr.min(), yhigh=yarr.max()
        )

        p.start_time -= self.spacing
        p.plen += 2 * self.spacing

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

    def draw_channels(self, *args, **kwargs):
        """
        Draws lines marking the channels

        """
        defaults = {"color": "k", "linewidth": 1.0, "zorder": -1}

        try:
            x0, x1 = kwargs["limits"]
            kwargs.pop("limits")
        except KeyError:
            x0, x1 = self.limits["xlow"], self.limits["xhigh"]

        defaults = {**defaults, **kwargs}

        for channel in args:
            if channel in self.params.keys():
                super().hlines(self.params[channel], x0, x1, **defaults)
            else:
                try:
                    super().hlines(channel, x0, x1, **defaults)
                except ValueError:
                    raise ValueError(
                        "Channel must be present in parameters, or must be a number"
                    )

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

        self.sequence = instruction

    def get_time(self, name=None, index=None):

        if name is not None:
            try:
                index_ = self.sequence.named_elements[name]
                x = self.sequence.elements[index_].start_time
            except KeyError:
                raise KeyError(f"Cannot find the element named {name}")

        elif index is not None:
            try:
                x = self.sequence.elements[index].start_time
            except KeyError:
                raise KeyError(f"Cannot find the element named {name}")

        else:
            raise ValueError("Either a name of a index must be supplied")

        return x

    def set_limits(self, limits=None):

        if limits is not None:
            self.limits = limits

        try:
            super().set_xlim(self.limits["xlow"], self.limits["xhigh"])
            super().set_ylim(self.limits["ylow"], self.limits["yhigh"])
        except IndexError:
            raise IndexError("limits should be given as [xlow, xhigh, ylow, yhigh]")

    def edit_limits(self, xlow=None, xhigh=None, ylow=None, yhigh=None):

        dx, dy = self.limits["dx"], self.limits["dy"]

        if (xlow is not None) and (xlow - dx < self.limits["xlow"]):
            self.limits["xlow"] = xlow - dx

        if (ylow is not None) and (ylow - dy < self.limits["ylow"]):
            self.limits["ylow"] = ylow - dy

        if (xhigh is not None) and (xhigh + dx > self.limits["xhigh"]):
            self.limits["xhigh"] = xhigh + dx

        if (yhigh is not None) and (yhigh + dy > self.limits["yhigh"]):
            self.limits["yhigh"] = yhigh + dy

        self.limits["dx"] = (self.limits["xhigh"] - self.limits["xlow"]) / 50
        self.limits["dy"] = (self.limits["yhigh"] - self.limits["ylow"]) / 50

        self.set_limits()
