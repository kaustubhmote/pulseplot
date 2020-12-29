# -*- coding: utf-8 -*-

import re
from collections import namedtuple
import json
import numpy as np
from matplotlib.patches import Polygon

TEXT_DEFAULTS = {"ha": "center", "va": "center"}

PAR = namedtuple("parameters", ["name", "type", "default", "pattern", "parents"])

# fmt: off
PARAMS = {
    "p":     PAR("plen",          float,  None,     r"(p=?[^lhdk ]+)?",   ["pulse"],),
    "pl":    PAR("power",         float,  None,     r"(pl=?[^ ]+)?",      ["pulse"],),
    "ph":    PAR("phase",         str,    None,     r"(ph=?[^ ]+)?",      ["pulse"],),
    "sp":    PAR("shape",         None,   None,     r"(sp=?[^ ]+)?",      ["pulse"],),
    "w":     PAR("wait",          None,   False,    r"(w)?",              ["pulse"],),
    "c":     PAR("centered",      None,   False,    r"(c[^h])?",          ["pulse"],),
    "kc":    PAR("keep_centered", None,   False,    r"(kc)?",             ["pulse"],),
    "fc":    PAR("facecolor",     str,    "white",  r"(fc=?[^ ]+)?",      ["pulse"],),
    "ec":    PAR("edgecolor",     str,    "black",  r"(ec=?[^ ]+)?",      ["pulse"],),
    "al":    PAR("alpha",         float,  1.0,      r"(al=?[^ ]+)?",      ["pulse"],),
    "h":     PAR("hatch",         str,    "",       r"(h=?[^ ]+)?",       ["pulse"],),
    "tr":    PAR("truncate",      None,   True,     r"(tr)?",             ["pulse"],),
    "np":    PAR("npoints",       int,    100,      r"(np=?[0-9]+)?",     ["pulse"],),
    "pdx":   PAR("phtxt_dx",      float,  0.0,      r"(pdx=?[^ ]+)?",     ["pulse"],),
    "pdy":   PAR("phtxt_dy",      float,  0.0,      r"(pdy=?[^ ]+)?",     ["pulse"],),
    "pkw":   PAR("phase_kw",      None,   "{}",     r"(pkw=?{.*?})?",     ["pulse"],),
    "d":     PAR("time",          float,  None,     r"(d=?[^ ]+)?",       ["delay"],),
    "st":    PAR("start_time",    float,  None,     r"(st=?[^ ]+)?",      ["pulse", "delay"],),
    "ch":    PAR("channel",       float,  None,     r"(ch=?[^ ]+)?",      ["pulse", "delay"],),
    "tx":    PAR("text",          str,    None,     r"(tx=?[^ ]+)?",      ["pulse", "delay"],),
    "tdx":   PAR("text_dx",       float,  0.0,      r"(tdx=?[^ ]+)?",     ["pulse", "delay"],),
    "tdy":   PAR("text_dy",       float,  0.0,      r"(tdy=?[^ ]+)?",     ["pulse", "delay"],),
    "tkw":   PAR("text_kw",       None,   "{}",     r"(tkw=?{.*?})?",     ["pulse", "delay"],),
    "n":     PAR("name",          str,    "",       r"(n=?[^p ])?",       ["pulse", "delay"],),
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
        arguments = [i + j for i, j in zip(arguments, m)]

    # parse and pick up values + cast to appropriate types
    for arg, (param, param_info) in zip(arguments, PARAMS.items()):
        if arg:
            try:
                # check external params dict
                value = params[arg]

                if callable(param_info.type):
                    userparams[param_info.name] = param_info.type(value)

                else:
                    userparams[param_info.name] = value

            except KeyError:

                # special case for Boolean params
                if arg == param:
                    userparams[param_info.name] = True

                else:

                    if arg[len(param)] == "=":
                        value = arg[len(param) + 1 :]

                    else:
                        value = arg[len(param) :]

                    if callable(param_info.type):
                        userparams[param_info.name] = param_info.type(value)

                    else:
                        userparams[param_info.name] = value
        else:
            userparams[param_info.name] = param_info.default

    return userparams


class Pulse(object):
    """
    Pulse object with annotations, including those
    for the phase

    """

    def __init__(self, *args, **params):
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

        args = parse_base(self.args)

        # check that the parsig is OK, remove things that are not required
        if args["time"] is not None:
            raise ValueError("A combination of a Pulse and a Delay is not allowed")

        if args["start_time"] is None:
            self.defer_start_time = True
            args["start_time"] = 0
        else:
            self.defer_start_time = False

        for k, v in PARAMS.items():
            if "pulse" not in v.parents:
                args.pop(v.name)

        # handle keywords from string
        for item in ["phase_kw", "text_kw"]:
            try:
                args[item] = json.loads(args[item])

            except json.decoder.JSONDecodeError:
                args[item] = json.loads(args[item].replace("'", '"'))

            except json.decoder.JSONDecodeError as e:
                raise ValueError(f"The input {args[item]} is not understood.")

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
            text = fr"$\phi_{self.phase}$"

        xpos = self.start_time + self.plen / 2 + self.phtxt_dx
        ypos = self.power + 0.1 + self.phtxt_dy

        phtxtparams = {"x": xpos, "y": ypos, "s": text}

        return {**phtxtparams, **TEXT_DEFAULTS, **self.phase_kw, **kwargs}

    def label_params(self, **ktextwargs):
        """
        Generates a dictionary to be passed
        into the ax.text function to put a tex
        annotation at an appropriate location.
        Generates x, y and s parameters from
        the pulse parameters. Everything is overwritten
        by the kwargs passed to this function.

        """
        xpos = self.start_time + self.plen / 2 + self.text_dx
        ypos = (self.power + self.channel) / 2 + self.text_dy

        labelparams = {"x": xpos, "y": ypos, "s": self.text}

        return {**labelparams, **TEXT_DEFAULTS, **self.text_kw, **kwargs}

    def __mul__(self, constant):
        """Increases the pulse length by a given factor"""

        try:
            self.plen *= constant
        except ValueError:
            raise ValueError("Pulse can only be multiplied with a constant")

    def __add__(self, constant):
        """Adds a constant to the pulse length"""

        try:
            self.plen += constant
        except ValueError:
            raise ValueError("Pulse can only be added to by a constant")

    def __pow__(self, constant):
        """Multiplies the power of a pulse by a constant"""

        try:
            self.power *= constant
        except ValueError:
            raise ValueError("Pulse Power can only be increased by constant factor")

    def get_shape(self):

        if callable(self.shape):
            shape_array = self.shape(np.linspace(0, 1, self.npoints))

        elif isinstance(self.shape, str):
            try:
                shape_array = shapedict[self.shape]
            except KeyError:
                raise KeyError(f"The shape {self.shape} not understood")

        else:
            shape_array = np.ones(self.npoints)

        return shape_array * self.power

    def time_array(self):

        if self.centered:
            start = self.start_time - self.plen / 2
        else:
            start = self.start_time

        return np.linspace(start, start + self.plen, self.npoints)

    def end_time(self):

        if self.centered:
            if self.keep_centered:
                return self.start_time + self.plen / 2

        else:
            return self.start_time + self.plen

    def patch(self, **kwargs):

        x = self.time_array()
        y = self.get_shape()

        if self.truncate:
            vertices = [[x[0], self.channel]]

        else:
            vertices = []

        for v in [[i, j + self.channel] for i, j in zip(x, y)]:
            vertices.append(v)

        if self.truncate:
            vertices.append([x[-1], self.channel])

        patch_params = {
            "facecolor": self.facecolor,
            "edgecolor": self.edgecolor,
            "hatch": self.hatch,
            "alpha": self.alpha,
        }

        patch_params = {**patch_params, **kwargs}

        pulse_patch = Polygon(vertices, **patch_params)

        return pulse_patch

    def render(self, ax, **kwargs):
        pulse_patch = self.patch(**kwargs)
        ax.add_patch(pulse_patch)

        return ax


class Delay(object):
    """
    Dealy object with annotations

    """

    def __init__(self, *args, **params):
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

        args = parse_base(self.args)

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

        for item in ["text_kw"]:
            try:
                args[item] = json.loads(args[item])

            except json.decoder.JSONDecodeError:
                args[item] = json.loads(args[item].replace("'", '"'))

            except json.decoder.JSONDecodeError as e:
                raise ValueError(f"The input {args[item]} is not understood.")

        self.__dict__ = {**self.__dict__, **args, **params}

    def label_params(self, **kwargs):
        """
        Generates a dictionary to be passed
        into the ax.text function to put a tex
        annotation at an appropriate location.
        Generates x, y and s parameters from
        the pulse parameters. Everything is overwritten
        by the kwargs passed to this function.

        """
        xpos = self.start_time + self.time / 2 + self.text_dx
        ypos = self.channel + self.text_dy + 0.1

        labelparams = {"x": xpos, "y": ypos, "s": self.text}

        return {**labelparams, **TEXT_DEFAULTS, **self.text_kw, **kwargs}

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


class PulseSeq:
    """Docstring for PulseSeq. """

    elements = {}

    def __init__(
        self, sequence, start_index=0,
    ):
        """TODO: to be defined.

        Parameters
        ----------
        *args : TODO
        **kwargs : TODO

        """

        if isinstance(sequence, str):
            self.args = [i for i in sequence.split("\n") if i.strip()]

        elif isinstance(sequence, list):
            self.args = sequence

        for i, arg in enumerate(self.args):

            if isinstance(arg, str):
                try:
                    element = Pulse(arg)
                except ValueError:
                    element = Delay(arg)
                except:
                    raise ValueError(f"Argument {arg} not understood.")

            elif isinstance(arg, Pulse) or isinstance(arg, Delay):
                    element = arg

            else:
                raise ValueError(f"Invalid argument type {type(arg)} ({arg}) for a pulse sequence element")

            if not element.name:
                self.elements[i + start_index] = element

            elif element.name in self.elements.keys():
                self.elements[f"{element.name}_{i}"] = element

            else:
                self.element[element.name] = element  