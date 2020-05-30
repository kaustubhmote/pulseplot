import re

PARAMS = {
    "p": ["plen", float, None],
    "pl": ["power", float, None],
    "ph": ["phase", str, None],
    "ch": ["channel", float, None],
    "sp": ["shape", str, None],
    "w": ["wait", None, False],
    "c": ["centered", None, False],
    "kc": ["keep_centered", None, False],
    "fc": ["facecolor", str, "white"],
    "ec": ["edgecolor", str, "black"],
    "al": ["alpha", float, 1.0],
    "tx": ["text", str, None],
    "d": ["time", float, None],
    "tr": ["truncate", None, True],
    "np": ["npoints", int, 100],
    "tdx": ["text_dx", float, 0.0],
    "tdy": ["text_dy", float, 0.0],
    "phpdx": ["phtxt_dx", float, 0.0],
    "phpdy": ["phtxt_dy", float, 0.0],
}


TYPES = {
    "pulse": ["plen", "power", "shape", "npoints", "truncate", "channel"],
    "pulse_params": ["facecolor", "edgecolor", "alpha"],
    "pulse_timing": ["wait", "centered", "keep_centered"],
    "text": ["text", "text_dx", "text_dy"],
    "phase": ["phase", "phtxt_dx", "phtxt_dy"],
    "delay": ["time", "channel"],
}


PATTERN = r"(p[^lh ]+)?(pl[^ ]+)?(ph[^p ]+)?(ch[^ ]+)?(sp[^ ]+)?(w)?(c)?(kc)?(fc[^ ]+)?(ec[^ ]+)?(al[^ ]+)?(tx[^ ]+)?(d[^ ]+)?(tr)?(np[0-9]+)?(tdx[^ ]+)?(tdy[^ ]+)?(phpdx[^ ]+)?(phpdy[^ ]+)?"


def collect(type_, params, extra_params):

    funclist = {
            "timing": collect_pulse_timing,
            "phase": collect_phase_params,
            "text": collect_text_params,
            "pulse": collect_pulse_params,
        }

    if params is None:
        pulse_timing = defaults
        for k in defaults.keys():
            if k in kwargs.keys():
                pulse_timing[k] = kwargs[k]
                kwargs.pop(k)

    else:
        pulse_timing = {**defaults, **pulse_timing}

    return funclist[type_](params, extra_params)


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

    for arg, (k, (name, type_, default)) in zip(arguments, PARAMS.items()):
        if arg:
            try:
                value = params[arg]
            except KeyError:
                if arg == k:
                    userparams[name] = True
                else:
                    value = arg[len(k) :]
                    userparams[name] = type_(value)
        else:
            userparams[name] = default

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
