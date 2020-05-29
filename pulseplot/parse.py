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


PATTERN = r"(p[^lh ]+)?(pl[^ ]+)?(ph[^p ]+)?(ch[^ ]+)?(sp[^ ]+)?(w)?(c)?(kc)?(fc[^ ]+)?(ec[^ ]+)?(al[^ ]+)?(tx[^ ]+)?(d[^ ]+)?(tr)?(np[0-9]+)?(tdx[^ ]+)?(tdy[^ ]+)?(phdx[^ ]+)?(phdy[^ ]+)?"


def collect(params, type_):
    """
    Collects all parameters of the specified type

    """
    type_params = {}
    for v in TYPES[type_]:
        type_params[v] = params[v]
        
    return type_params


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
        p = collect(userparams, type_)
        p["_type"] = type_        
        el[type_] = p

    if el["pulse"]["plen"] is not None:
        el.pop("delay")
        for n in ["pulse_params", "pulse_timing",]:
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


    """
    p = parse_base(string, params)
    
    return sort(p)





def parse_sim(string, params=None):
    """
    Parse simultaneous instructions, i.e., 
    all instructions that start at the same time

    """
    instructions = []
    for s in string.strip().split(";"):
        instructions.append(parse_single(s, params))

    return instructions


def parse_multiline(string, params=None):
    """
    Parse a multiline pulse-sequence

    """
    instructions = []
    for s in string.strip().split("\n"):
        instructions.append(parse_sim(s, params))

    return instructions
