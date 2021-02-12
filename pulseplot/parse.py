# -*- coding: utf-8 -*-

import json
import re
from collections import namedtuple
from warnings import warn

import numpy as np
from matplotlib.patches import Polygon

PULSE_DEFAULTS = {"power": 1.0, "channel": 0.0}
TEXT_DEFAULTS = {"fontsize": 10, "ha": "center", "va": "center"}

PAR = namedtuple("parameters", ["name", "type", "default", "pattern", "parents"])

# fmt: off
PARAMS = {
    "p":     PAR("plen",            float,  None,     r"(p=?[^lhdkf ]+)?",              ["pulse"],),
    "pl":    PAR("power",           float,  1.0,      r"(pl=?[^ ]+)?",                  ["pulse", "delay"],),
    "ph":    PAR("phase",           str,    None,     r"(ph=?[^ ]+)?",                  ["pulse", "delay"],),
    "sp":    PAR("shape",           None,   None,     r"(sp=?[^ ]+)?",                  ["pulse", "delay"],),
    "w":     PAR("wait",            bool,   False,    r"(w)?",                          ["pulse", "delay"],),
    "c":     PAR("centered",        bool,   False,    r"(c[^l])?",                      ["pulse", "delay"],),
    "kc":    PAR("keep_centered",   bool,   False,    r"(kc)?",                         ["pulse", "delay"],),
    "fc":    PAR("facecolor",       str,    "white",  r"(fc=?[^ ]+)?",                  ["pulse", "delay"],),
    "ec":    PAR("edgecolor",       str,    "black",  r"(ec=?[^ ]+)?",                  ["pulse", "delay"],),
    "al":    PAR("alpha",           float,  1.0,      r"(al=?[^ ]+)?",                  ["pulse", "delay"],),
    "h":     PAR("hatch",           str,    "",       r"(h=?[^ ]+)?",                   ["pulse", "delay"],),
    "tr":    PAR("truncate_off",    bool,   False,    r"(troff)?",                      ["pulse", "delay"],),
    "np":    PAR("npoints",         int,    100,      r"(np=?[0-9]+)?",                 ["pulse", "delay"],),
    "pdx":   PAR("phtxt_dx",        float,  0.0,      r"(pdx=?[^ ]+)?",                 ["pulse", "delay"],),
    "pdy":   PAR("phtxt_dy",        float,  0.0,      r"(pdy=?[^ ]+)?",                 ["pulse", "delay"],),
    "pfs":   PAR("ph_fontsize",     float,  15.0,     r"(pfs=?[^ ]+)?",                 ["pulse", "delay"],),
    "pkw":   PAR("phase_kw",        str,   "{}",      r"(pkw=?{.*?})?",                 ["pulse", "delay"],),
    "o":     PAR("open",            bool,   False,    r"(o)?",                          ["pulse", "delay"],),  
    "d":     PAR("time",            float,  None,     r"(d=?[^ ]+)?",                   ["delay",]),
    "st":    PAR("start_time",      float,  None,     r"(st=?[^ ]+)?",                  ["pulse", "delay"],),
    "f":     PAR("channel",         float,  0.0,      r"(f=?[^c ]+)?",                  ["pulse", "delay"],),
    "tx":    PAR("text",            str,    None,     r"(tx[^`]=?[^ ]+|tx=?`.*?`)?",    ["pulse", "delay"],),
    "tdx":   PAR("text_dx",         float,  0.0,      r"(tdx=?[^ ]+)?",                 ["pulse", "delay"],),
    "tdy":   PAR("text_dy",         float,  0.0,      r"(tdy=?[^ ]+)?",                 ["pulse", "delay"],),
    "tkw":   PAR("text_kw",         str,   "{}",      r"(tkw=?{.*?})?",                 ["pulse", "delay"],),
    "tfs":   PAR("text_fontsize",   float,  15.0,     r"(tfs=?[^ ]+)?",                 ["pulse", "delay"],),
    "n":     PAR("name",            str,    "",       r"(n=?[^p ]+)?",                  ["pulse", "delay"],),
    "skw":   PAR("style_kw",        str,    "{}",     r"(skw=?{.*?})?",                 ["pulse", "delay"],),
}
# fmt: on

PATTERN = "".join([v.pattern for k, v in PARAMS.items()])


def parse_base(instructions, params=None):
    """
    Basic parsing of a single line of instructions
    using regexes

    """
    arguments = [""] * len(PARAMS)

    userparams = {}

    if params is None:
        params = {}

    # match and squash
    matches = re.findall(PATTERN, instructions)
    for m in matches:
        for i, _ in enumerate(arguments):
            value = m[i]
            if value:
                arguments[i] = value

    # parse and pick up values + cast to appropriate types
    for arg, (param, param_info) in zip(arguments, PARAMS.items()):
        if arg:
            try:
                # check external params dict
                value = params[arg]

                if callable(param_info.type):
                    try:
                        userparams[param_info.name] = param_info.type(value)
                    except ValueError:
                        raise ValueError(
                            f"Cannot cast {arg} in the appropriate type {param_info.type} "
                        )
                else:
                    userparams[param_info.name] = value

            except KeyError:

                # special case for Boolean params
                if arg == param:
                    userparams[param_info.name] = not param_info.default

                else:
                    if arg[len(param)] == "=":
                        value = arg[len(param) + 1 :]
                    else:
                        value = arg[len(param) :]

                    if callable(param_info.type):
                        try:
                            userparams[param_info.name] = param_info.type(value)
                        except ValueError:
                            raise ValueError(
                                f"Cannot cast {arg} in the appropriate type {param_info.type}"
                            )
                    else:
                        userparams[param_info.name] = value
        else:
            userparams[param_info.name] = param_info.default

    return userparams


class Pulse(object):
    """
    Pulse object
    """

    def __init__(
        self, *args, external_params={}, **params,
    ):
        """TODO: to be defined.

        Parameters
        ----------
        *args : TODO
        **kwargs : TODO


        """
        try:
            self.args = " ".join(i for i in args)
        except TypeError as e:
            raise TypeError("All arguments without a keyword should be strings")

        args = parse_base(self.args, external_params)

        # check that the parsing is OK, remove things that are not required
        if args["time"] is not None:
            raise ValueError("A combination of a Pulse and a Delay is not allowed")

        if args["start_time"] is None:
            self.defer_start_time = True
            args["start_time"] = 0
        else:
            self.defer_start_time = False

        for _, v in PARAMS.items():
            if "pulse" not in v.parents:
                args.pop(v.name)

        # handle keywords from string
        for item in ["phase_kw", "text_kw", "style_kw"]:
            try:
                # maybe json needs to be replaced with ast.literal_eval?
                args[item] = json.loads(args[item])

            except json.decoder.JSONDecodeError:
                args[item] = json.loads(args[item].replace("'", '"'))

            except json.decoder.JSONDecodeError as e:
                raise ValueError(f"The input {args[item]} is not understood.")

        try:
            if args["text"].startswith("`") and args["text"].endswith("`"):
                args["text"] = args["text"][1:-1]
        except AttributeError:
            pass

        if args["shape"] is not None:
            if args["shape"].startswith("fid"):
                args["truncate_off"] = True
                args["open"] = True

        self.__dict__ = {**self.__dict__, **args, **params}

    def phase_params(self, **kwargs):
        """
        Generates a dictionary to be passed
        into the ax.text function to put a phase
        annotation at an appropriate location.
        Generates x, y and s parameters from
        the pulse parameters. Everything is overwritten
        by the kwargs passed to this function.

        """
        if self.phase.startswith("_"):
            text = fr"{self.phase[1:]}"

        else:
            text = fr"$\phi_{{{self.phase}}}$"

        p = self.patch()
        center = int(self.npoints // 2)
        xpos = p.xy[:, 0][center] + self.phtxt_dx
        ypos = p.xy[:, 1][center] + self.phtxt_dy + 0.15

        phtxtparams = {"x": xpos, "y": ypos, "s": text, "fontsize": self.ph_fontsize}

        return {**TEXT_DEFAULTS, **phtxtparams, **self.phase_kw, **kwargs}

    def label_params(self, **kwargs):
        """
        Generates a dictionary to be passed
        into the ax.text function to put a tex
        annotation at an appropriate location.
        Generates x, y and s parameters from
        the pulse parameters. Everything is overwritten
        by the kwargs passed to this function.

        """
        p = self.patch()
        center = int(self.npoints // 2)
        xpos = p.xy[:, 0][center] + self.text_dx
        ypos = p.xy[:, 1][center] / 2 + p.xy[:, 1].min() / 2 + self.text_dy

        # xpos = self.start_time + self.plen / 2 + self.text_dx
        # ypos = self.power / 2 + self.channel + self.text_dy

        labelparams = {
            "x": xpos,
            "y": ypos,
            "s": self.text,
            "fontsize": self.text_fontsize,
        }

        return {**TEXT_DEFAULTS, **labelparams, **self.text_kw, **kwargs}

    def __mul__(self, constant):
        """
        Increases the pulse length by a given factor

        """
        try:
            self.plen *= constant
        except ValueError:
            raise ValueError("Pulse can only be multiplied with a constant")

    def __add__(self, constant):
        """
        Adds a constant to the pulse length

        """
        try:
            self.plen += constant
        except ValueError:
            raise ValueError("Pulse can only be added to by a constant")

    def __pow__(self, constant):
        """
        Multiplies the power of a pulse by a constant

        """
        try:
            self.power *= constant
        except ValueError:
            raise ValueError("Pulse Power can only be increased by constant factor")

    def get_shape(self):
        """
        Returns the shape of the pulse on an array from 0 to 1

        """
        if callable(self.shape):
            shape_array = self.shape(np.linspace(0, 1, self.npoints))

        elif isinstance(self.shape, str):
            shape_array = Shape(self.shape, self.npoints).get_shape()

        else:
            shape_array = np.ones(self.npoints)

        return shape_array * self.power

    def time_array(self):
        """
        Gets the x-axis for the pulse

        """
        if self.centered:
            start = self.start_time - self.plen / 2
        else:
            start = self.start_time

        return np.linspace(start, start + self.plen, self.npoints)

    def end_time(self):
        """
        Gets the time point where the pulse is supposed to end
        Depending on whether the wait of keep centered keywords
        are set, it gives the appropriate end time

        """
        if self.centered:
            if self.keep_centered:
                return self.start_time

            elif self.wait:
                return self.start_time - self.plen / 2

            else:
                return self.start_time + self.plen / 2

        else:
            if self.wait:
                return self.start_time

            else:
                return self.start_time + self.plen

    def patch(self, **kwargs):
        """
        Gets the matplotlib.patches.Polygon patch for the pulse
        to be added on to an matplotlib Axes object

        """
        x = self.time_array()
        y = self.get_shape()

        if not self.truncate_off:
            vertices = [[x[0], self.channel]]

        else:
            vertices = []

        for v in [[i, j + self.channel] for i, j in zip(x, y)]:
            vertices.append(v)

        if not self.truncate_off:
            vertices.append([x[-1], self.channel])

        patch_params = {
            "facecolor": self.facecolor,
            "edgecolor": self.edgecolor,
            "hatch": self.hatch,
            "alpha": self.alpha,
            **self.style_kw,
        }

        patch_params = {**patch_params, **kwargs}

        pulse_patch = Polygon(vertices, closed=not self.open, **patch_params)

        return pulse_patch

    def render(self, ax, **kwargs):
        """
        Adds a polygon patch of the pulse to the
        given axes object

        """
        pulse_patch = self.patch(**kwargs)
        ax.add_patch(pulse_patch)

        return ax


class Delay(Pulse):
    """
    Dealy object with annotations

    """

    def __init__(self, *args, external_params={}, **params):
        """TODO: to be defined.

        Parameters
        ----------
        *args : TODO
        **kwargs : TODO


        """
        try:
            self.args = " ".join(i for i in args)
        except TypeError as e:
            raise TypeError("All arguments without a keyword should be strings")

        args = parse_base(self.args, external_params)

        # check that the parsig is OK, remove things that are not required
        if args["plen"] is not None:
            raise ValueError("A combination of a Pulse and a Delay is not allowed")

        if args["start_time"] is None:
            self.defer_start_time = True
            args["start_time"] = 0
        else:
            self.defer_start_time = False

        for k, v in PARAMS.items():
            if "delay" not in v.parents:
                args.pop(v.name)

        for item in ["text_kw", "phase_kw", "style_kw"]:
            try:
                args[item] = json.loads(args[item])

            except json.decoder.JSONDecodeError:
                args[item] = json.loads(args[item].replace("'", '"'))

            except json.decoder.JSONDecodeError as e:
                raise ValueError(f"The input {args[item]} is not understood.")

        self.__dict__ = {**self.__dict__, **args, **params}

        self.plen = self.time
        self.facecolor = "none"
        self.edgecolor = "none"
        self.power = PULSE_DEFAULTS["power"]

    def __mul__(self, constant):
        """Increases the delay by a given factor"""

        try:
            self.time *= constant
        except ValueError:
            raise ValueError("Pulse can only be multiplied with a constant")

    def __add__(self, constant):
        """Adds a constant to the pulse length"""

        try:
            self.time += constant
        except ValueError:
            raise ValueError("Pulse can only be added to by a constant")


class PulseSeq(object):
    """Docstring for PulseSeq. """

    def __init__(
        self, sequence, external_params={},
    ):
        """TODO: to be defined.

        Parameters
        ----------
        *args : TODO
        **kwargs : TODO

        """
        self.elements = []
        self.named_elements = {}
        self.input_string = ""

        if isinstance(sequence, str):
            self.input_string = sequence
            self.args = [i for i in sequence.split("\n") if i.strip()]
            self.args = [i.split("#")[0] for i in self.args if i.split("#")[0]]

        elif isinstance(sequence, list):
            self.args = sequence

        for i, arg in enumerate(self.args):
            if isinstance(arg, str):
                try:
                    element = Pulse(arg, external_params=external_params)

                except ValueError:
                    element = Delay(arg, external_params=external_params)

                except:
                    raise ValueError(f"Argument {arg} not understood.")

            elif isinstance(arg, Pulse) or isinstance(arg, Delay):
                element = arg

            else:
                raise ValueError(
                    f"Invalid argument type {type(arg)} ({arg}) for a pulse sequence element"
                )

            self.elements.append(element)

            if element.name:
                self.named_elements[element.name] = i

    def edit(self, index=None, name=None, **kwargs):

        if index is not None:
            self.elements[index].__dict__.update(kwargs)

        elif name is not None:
            try:
                index = self.named_elements[name]
            except KeyError:
                raise KeyError(f"Element {name} not found")

            self.elements[index].__dict__.update(kwargs)

    def __len__(self):
        return len(self.elements)


class Shape(object):
    """ Pulse shapes """

    def __init__(self, name, npoints):
        """shape object with a name and the number of points"""

        self.input = str(name)
        self.npoints = int(npoints)
        self.xscale = np.linspace(0, 1, npoints)

        allpars = self.guess_pars()
        self.name = allpars[0]
        self.pars = allpars[1:]

    def guess_pars(self):
        """Guesses the shape name and any parameters separated by _"""
        new_pars = ["", None, None]
        pars = self.input.split("_")

        try:
            new_pars[0] = str(pars[0])
            new_pars[1] = float(pars[1])
            new_pars[2] = float(pars[2])
        except IndexError:
            pass
        except ValueError:
            raise ValueError(f"Did not understand the show {self.input}")

        return new_pars

    def normalize(self, array, high=1, low=0):

        array -= array.min()
        array /= array.max()
        array *= high - low
        array += low

        return array

    def get_shape(self):
        """Returns the shape after introspecting the passed parameters"""
        try:
            return self.__getattribute__(self.name)(*self.pars)
        except AttributeError:
            warn(
                f"Did not understand the shape {self.name}. Changing to a square shape"
            )
            return self.square()

    def square(self):
        """Square shaped pulse, use here as a fallback"""
        return np.ones(self.npoints)

    def gauss(self, x0, sigma, *args, **kwargs):
        "Gaussian shaped pulse"
        if x0 is None:
            x0 = 0.5
        if sigma is None:
            sigma = 1 / 6.0

        s = np.exp(-((self.xscale - x0) ** 2) / 2 / sigma ** 2)

        return self.normalize(s)

    def ramp(self, percent, *args, **kwargs):
        """Linear ramp"""
        if percent is None:
            percent = 40

        s = np.linspace(1 - abs(percent) / 100, 1, self.npoints)

        if percent > 0:
            return s
        else:
            return s[::-1]

    def tan(self, percent, curvature, *args, **kwargs):
        """Adiabatic (Tangential) Shape"""
        if percent is None:
            percent = 50
        if curvature is None:
            curvature = 0.1

        p = abs(percent) / 100
        s = np.sinh((self.xscale - 0.5) / curvature)
        s = self.normalize(s, high=1, low=1 - p)

        if percent > 0:
            return s
        else:
            return s[::-1]

    def fid(self, freq, decay, *args, **kwargs):
        """Free induction decay"""
        if freq is None:
            freq = 2 * np.pi * 10
        else:
            freq *= 2 * np.pi

        if decay is None:
            decay = 5

        s = np.exp(1j * freq * self.xscale - decay * self.xscale).real

        return self.normalize(s, high=1.0, low=0.0)

    def fid2(self, freq, decay, *args, **kwargs):
        """A shifted fid"""
        s = self.fid(freq, decay, *args, **kwargs)
        s += (np.random.random(self.npoints) - 0.5) * 0.1
        return self.normalize(s, high=1.0, low=0.0)

    def grad(self, rise, *args, **kwargs):
        """Gradient shape"""
        if rise is None:
            rise = 8

        s = np.exp(-((self.xscale - 0.5) ** rise) / 0.5 ** rise)

        return self.normalize(s)

    def sine(self, *args, **kwargs):
        """Single sine shape"""
        x = np.linspace(0, np.pi, self.npoints)

        return np.sin(x)

    def grad2(self, *args, **kwargs):
        """Gradient: uses the sine shape instead of actual gradient shape"""
        return self.sine(*args, **kwargs)
