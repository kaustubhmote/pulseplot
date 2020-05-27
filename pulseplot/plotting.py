"""
Utilities for making plots

"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.projections import register_projection
from parse import parse_multiline, parse_single


def pulseplot(*args, **kwargs):
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



def shaped_pulse(start, length, shape=None, npoints=100):

    x = np.linspace(start, start+length, npoints)

    if shape is None:
        y = lambda x: 1 + 0.0*x

    elif is callable(func):
        y = shape(x)

    elif isinstance(shape, (list, tuple)):
        if len(shape) == x.shape[-1]:
            y = shape
        else:
            raise ValueError("the given shape is incompatible with the time array")

    elif isinstance(shape, np.ndarray):
        if shape.shape[-1] == x.shape[-1]:
        else:
            raise ValueError("the given shape is incompatible with the time array")

            

def text_wrapper(self, **kwargs):
    """
    Wrapper around the text command

    """
    if ("x" not in kwargs) or ("y" not in kwargs):
        raise ValueError("Position for the text is not understood")
    else:
        kwargs["s"] = text

    if "dx" in kwargs:
        x += kwargs["dx"]
        kwargs.pop("dx")
    if "dy" in kwargs:
        y += kwargs["dy"]
        kwargs.pop["dy"]

    if ("ha" not in kwargs) and ("horizontalalignemnt" not in kwargs):
        kwargs["ha"] = "center"
    if ("va" not in kwargs) and ("verticalalignment" not in kwargs):
        kwargs["va"] = "center"

    return kwargs
    

def phasetext(self, text=None, **kwargs):
    """
    Annotate a phase 

    """
    if text is None:
        text = ""
    else:
        text = str(text)

    if text.startswith("_"):
        text = text[1:]
    else:
        text = r"$\phi_{" + text + "}$"

    kwargs["s"] = text

    return text_wrapper(**kwargs)

        
class PulseProgram(plt.Axes):
    """
    A class that defines convinience functions for
    plotting elements of a NMR pulse squence on a 
    matplotlib axes object.

    Usage
    -----
    
    >>> from pulseplot import pulseplot 
    >>> fig, ax = pulseplot()
    >>> ax.pulse("p1 pl1 ph1 :1")
    >>> ax.delay(2)
    >>> ax.pulse("p2 pl1 ph2 :1")
    >>> ax.delay(2)
    >>> ax.fid(time=4, channel=1, amp=0.2, phase=2)
    >>> plt.show()

    """
    name = "PulseProgram"
    channels = []
    time = 0.0
    params = {}
    elements = []

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

    def pulseseq(self, instruction, **kwargs):
        seq = parse_multiline(instruction, self.params)
        start = self.time
        for line in seq:
            time_tracker = []
            
            for sim in line:
                if sim["type"] == "pulse":
                    self.pulse(**sim, **kwargs)

                elif sim["type"] == "delay":
                    self.delay(**sim, **kwargs)

                time_tracker.append(self.time)
                self.time = start

            elapsed = max(time_tracker)
            self.time = start + elapsed


    def pulse(
        self,
        parse=None,
        plen=0.2,
        power=0.5,
        channel=0,
        shape=None,
        wait=False,
        centered=False,
        keep_centered=True,
        points=100,
        start_time=None,
        truncate=True,
        fill=None,
        phase=None,
        phase_params={},
        text=None,
        text_params={},
        _type="pulse",
        **kwargs,
    ):

        if isinstance(parse, str):
            super().pulseseq(parse, **kwargs)

        assert _type == "pulse"

        default_fill = {
            "edgecolor": "black",
            "facecolor": "white",
            "alpha": 1.0,
        }


        if fill is None:
            fill = default_fill
        else:
            fill = {**default_fill, **fill}


        # on which channel
        if channel not in self.channels:
            self.channels.append(channel)

        # timing
        if start_time is None:
            if centered:
                start_time = self.time - plen / 2
            else:
                start_time = self.time

        end_time = start_time + plen

        # adjust RF for channel
        power += channel

        # make an xscale for plotting the shape
        xscale = np.linspace(start_time, end_time, points)

        # if square pulse
        if shape is None:
            shape = power * np.ones(points)

        # an arbitrary shape given by a 1D function
        elif callable(shape):
            shape = shape(xscale - start_time)
            shape = power * shape + channel
        else:
            try:
                # given shape
                xscale = np.linspace(start_time, end_time, shape.shape[-1])
            except:
                try:
                    xscale = np.linspace(start_time, end_time, len(shape))
                except:
                    raise TypeError("Shape not understood")

        # plot the shape
        super().plot(xscale, shape, color=fill["edgecolor"], **kwargs)

        # shape fill
        if len(fill):
            super().fill_between(
                xscale, shape, channel * np.ones(shape.shape[-1]), 
                **{**fill, **{"edgecolor": "none"}}
            )

        # draw vertical lines down to the channel
        if truncate:
            super().vlines(
                start_time, channel, shape[0], color=fill["edgecolor"], **kwargs
            )
            super().vlines(
                end_time, channel, shape[-1], color=fill["edgecolor"], **kwargs
            )

        # move to the end time
        if not wait:
            self.time = end_time
        if centered and keep_centered:
            self.time = start_time + plen / 2

        # phase text
        if phase is not None:
            options = phase_params.keys()
            pos = {}

            if "x" not in options:
                pos["x"] = start_time + plen / 2

            if "y" not in options:
                pos["y"] = shape[int(len(shape)//2)] + 0.1

            if "s" not in options:
                if isinstance(phase, str):
                    if phase.startswith("_"):
                        pos["s"] = phase[1:]
                    else:
                        pos["s"] = f"$\mathrm{{\phi}}_{{{phase}}}$"
                else:
                    pos["s"] = f"$\mathrm{{\phi}}_{{{phase}}}$"

            if "horizontalalignment" not in options:
                pos["horizontalalignment"] = "center"

            if "verticalalignment" not in options:
                pos["verticalalignment"] = "center"

            super().text(**pos, **phase_params)

        # arbitrary text annotation
        if text is not None:
            pos = {}
            options = text_params.keys()
            if "x" not in options:
                pos["x"] = start_time + plen / 2
            if "y" not in options:
                pos["y"] = shape[int(len(shape)//2)] / 2 + channel / 2
            if "horizontalalignment" not in options:
                pos["horizontalalignment"] = "center"
            if "verticalalignment" not in options:
                pos["verticalalignment"] = "center"
            pos["s"] = text
            super().text(**pos, **text_params)

    def delay(self, time, type="delay", channel=None, text=None, text_params={}):

        assert type == "delay"

        if channel is not None:
            if "channel" not in text_params.keys():
                text_params["channel"] = channel

        if text is not None:
            options = text_params.keys()
            pos = {}
            if "x" not in options:
                pos["x"] = self.time + time / 2
            if "y" not in options:
                if "channel" not in options:
                    pos["y"] = self.channels[0] + 0.1
                else:
                    pos["y"] = text_params["channel"] + 0.1
                    text_params.pop("channel")
            if "horizontalalignment" not in options:
                pos["horizontalalignment"] = "center"
            pos["s"] = text
            super().text(**pos, **text_params)

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
