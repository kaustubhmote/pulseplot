import re
from collections import namedtuple

parameters = namedtuple("parameters", ["name", "type", "default", "pattern"])

PARAMS = {
    "p": parameters("plen", float, None, r"(p[^lh ]+)?"),
    "pl": parameters("power", float, None, r"(pl[^ ]+)?",),
    "ph": parameters("phase", str, None, r"(ph[^p ]+)?",),
    "ch": parameters("channel", float, None, r"(ch[^ ]+)?",),
    "sp": parameters("shape", None, None, r"(sp[^ ]+)?",),
    "w": parameters("wait", None, False, r"(w)?",),
    "c": parameters("centered", None, False, r"(c[^h])?",),
    "kc": parameters("keep_centered", None, False, r"(kc)?",),
    "fc": parameters("facecolor", str, "white", r"(fc[^ ]+)?",),
    "ec": parameters("edgecolor", str, "black", r"(ec[^ ]+)?",),
    "al": parameters("alpha", float, 1.0, r"(al[^ ]+)?",),
    "tx": parameters("text", str, None, r"(tx[^ ]+)?",),
    "d": parameters("time", float, None, r"(d[^ ]+)?",),
    "tr": parameters("truncate", None, True, r"(tr)?",),
    "np": parameters("npoints", int, 100, r"(np[0-9]+)?",),
    "tdx": parameters("text_dx", float, 0.0, r"(tdx[^ ]+)?",),
    "tdy": parameters("text_dy", float, 0.0, r"(tdy[^ ]+)?",),
    "phpdx": parameters("phtxt_dx", float, 0.0, r"(phpdx[^ ]+)?",),
    "phpdy": parameters("phtxt_dy", float, 0.0, r"(phpdy[^ ]+)?",),
}


PATTERN = "".join([v.pattern for v in PARAMS.values()])

TYPES = {
    "pulse": ["plen", "power", "shape", "npoints", "truncate", "channel"],
    "pulse_params": ["facecolor", "edgecolor", "alpha"],
    "pulse_timing": ["wait", "centered", "keep_centered"],
    "text": ["text", "text_dx", "text_dy"],
    "phase": ["phase", "phtxt_dx", "phtxt_dy"],
    "delay": ["time", "channel"],
}


def sort(userparams):
    """
    Parses a single line

    Parameters
    ----------
    instructions : str
        A single

    """
    if (userparams["plen"] is not None) and (userparams["time"] is not None):
        raise ValueError("Pulses and delays cannot be mixed")

    el = {}
    for type_ in TYPES.keys():
        p = collect_userparams(userparams, type_)
        p["_type"] = type_
        el[type_] = p

    if el["pulse"]["plen"] is not None:
        el.pop("delay")
        for n in [
            "pulse_params",
            "pulse_timing",
        ]:
            el["pulse"][n] = el[n]
            el[n].pop("_type")
            el.pop(n)

    else:
        for n in ["pulse_params", "pulse_timing", "pulse"]:
            el.pop(n)

    if el["text"]["text"] is None:
        el.pop("text")

    if el["phase"]["phase"] is None:
        el.pop("phase")

    return el


def parse_base(instructions, params=None):
    """
    Basic parsing of a single line of instructions
    using regexes

    """
    arguments = [""] * len(PARAMS)
    userparams = {}
    if params is None:
        params = {}

    matches = re.findall(PATTERN, instructions)

    for m in matches:
        arguments = [i + j for i, j in zip(arguments, m)]

    for arg, (k, v) in zip(arguments, PARAMS.items()):
        if arg:
            try:
                value = params[arg]
                if callable(v.type):
                    userparams[v.name] = v.type(value)
                else:
                    userparams[v.name] = value

            except KeyError:
                if arg == k:
                    userparams[v.name] = True
                else:
                    value = arg[len(k) :]
                    if callable(v.type):
                        userparams[v.name] = v.type(value)
                    else:
                        userparams[v.name] = value
        else:
            userparams[v.name] = v.default

    return userparams


def parse_single(string, params=None):
    """
    Parse a single line of instructions and sorting
    according to the type of the instruction

    """
    p = parse_base(string, params)

    return sort(p)


def parse_multiline(string, params=None):
    """
    Parse a multiline pulse-sequence

    """
    instructions = []
    for s in string.strip().split("\n"):
        instructions.append(parse_single(s, params))

    return instructions


def collect_userparams(params, type_):
    """
    Collects all parameters of the specified type

    """
    type_params = {}
    for v in TYPES[type_]:
        type_params[v] = params[v]

    return type_params


def collect_pulse_timings(pulse_timing, kwargs):
    """
    Collects all keywrods associated with pulse
    timing instructions into a dictionary and
    returns the new dictionary and the remaining
    items

    """
    defaults = {
        "wait": False,
        "centered": False,
        "keep_centered": False,
    }

    if pulse_timing is None:
        pulse_timing = defaults
        for k in defaults.keys():
            if k in kwargs.keys():
                pulse_timing[k] = kwargs[k]
                kwargs.pop(k)

    else:
        pulse_timing = {**defaults, **pulse_timing}

    return pulse_timing, kwargs


def collect_pulse_params(pulse_params, kwargs, truncate):
    """
    Collect arguments for pulse params 
    These are passed on to the Polygon patch or
    the Line2D

    """
    if truncate:
        defaults = {
            "facecolor": "white",
            "edgecolor": "black",
            "alpha": 1.0,
            "linewidth": 2.0,
        }
    else:
        defaults = {
            "color": "black",
            "alpha": 1.0,
            "linewidth": 2.0,
        }

    if pulse_params is None:
        pulse_params = defaults
        for k in defaults.keys():
            if k in kwargs.keys():
                pulse_params[k] = kwargs[k]
                kwargs.pop(k)
    else:
        pulse_params = {**defaults, **pulse_params}

    return pulse_params, kwargs


def collect_phase_params(phase_params, kwargs):

    defaults = {
        "phase": None,
        "phtxt_dx": 0.0,
        "phtxt_dy": 0.0,
    }

    if phase_params is None:
        phase_params = defaults
        for k in defaults.keys():
            if k in kwargs.keys():
                phase_params[k] = kwargs[k]
                kwargs.pop(k)

    else:
        phase_params = {**defaults, **phase_params}

    phase_params["dx"] = phase_params["phtxt_dx"]
    phase_params.pop("phtxt_dx")
    phase_params["dy"] = phase_params["phtxt_dy"]
    phase_params.pop("phtxt_dy")

    return phase_params, kwargs


def collect_text_params(text_params, kwargs):

    defaults = {
        "text": None,
        "text_dx": 0.0,
        "text_dy": 0.0,
        "channel": None,
    }

    if text_params is None:
        text_params = defaults
        for k in defaults.keys():
            if k in kwargs.keys():
                text_params[k] = kwargs[k]
                kwargs.pop(k)

    else:
        text_params = {**defaults, **text_params}

    text_params["dx"] = text_params["text_dx"]
    text_params.pop("text_dx")
    text_params["dy"] = text_params["text_dy"]
    text_params.pop("text_dy")

    return text_params, kwargs


def text_wrapper(**kwargs):
    """
    Wrapper around the text command

    """
    if ("x" not in kwargs) or ("y" not in kwargs):
        raise ValueError("Position for the text is not understood")

    else:
        if "phase" in kwargs.keys():
            kwargs["s"] = kwargs["phase"]
            kwargs.pop("phase")
        elif "text" in kwargs.keys():
            kwargs["s"] = kwargs["text"]
            kwargs.pop("text")

    if "dx" in kwargs:
        kwargs["x"] += kwargs["dx"]
        kwargs.pop("dx")

    if "dy" in kwargs:
        kwargs["y"] += kwargs["dy"]
        kwargs.pop("dy")

    if ("ha" not in kwargs) and ("horizontalalignemnt" not in kwargs):
        kwargs["ha"] = "center"
    if ("va" not in kwargs) and ("verticalalignment" not in kwargs):
        kwargs["va"] = "center"

    return kwargs


def phasetext(phase=None):
    """
    Annotate a phase 

    """
    if phase is None:
        phase = ""
    else:
        phase = str(phase)

    if phase.startswith("_"):
        phase = phase[1:]
    else:
        phase = r"$\mathrm{\phi_{" + phase + "}}$"

    return phase
