import re

# {parameter name : [full name, type, default]}
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
    "tpdx": ["text_dx", float, 0.0],
    "tpdy": ["text_dy", float, 0.0],
    "phpdx": ["phtxt_dx", float, 0.0],
    "phpdy": ["phtxt_dy", float, 0.0],
}


PATTERN = r"(p[^lh ]+)?(pl[^ ]+)?(ph[^p ]+)?(ch[^ ]+)?(sp[^ ]+)?(w)?(c)?(kc)?(fc[^ ]+)?(ec[^ ]+)?(al[^ ]+)?(tx[^ ]+)?(d[^ ]+)?(tr)?(np[0-9]+)?(tpdx[^ ]+)?(tpdy[^ ]+)?(phdx[^ ]+)?(phdy[^ ]+)?"
    


def parse_single(instructions, params=None):
    """
    Parses a single line

    Parameters
    ----------
    instructions : str
        A single

    """ 
    arguments = [""] * len(PARAMS)
    userparams = {}
    if params is None:
        params = {}

    matches = re.findall(PATTERN, instructions)

    for m in matches:
        arguments = [i+j for i, j in zip(arguments, m)]

    for arg, (k, (name, type_, default)) in zip(arguments, PARAMS.items()):
        if arg:
            try:
                value = params[arg]
            except KeyError:
                if arg == k:
                    userparams[name] = True
                else:
                    value = arg[len(k):]
                    userparams[name] = type_(value)
        else:
            userparams[name] = default

    if userparams["plen"] is not None:
        userparams["_type"] = "pulse"
        if userparams["time"] is not None:
            raise ValueError("Pulses and delays cannot be mixed")
        userparams.pop("time")

    elif userparams["time"] is not None:
        userparams["_type"] = "delay"
        for (k, _, _) in PARAMS.values():
            if k not in ["time", "text", "channel", "text_dx", "text_dy"]:
                userparams.pop(k)

    return userparams
        

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
