from pulseplot import *


test_string = r"""p1 pl1 ph1 ch2
d1 ch1 tx$\\tau$
d1 ch1 txTEST tdx0.1 tdy0.3
p1 pl1 ph1 ch8 fcr ecg al0.33
p3 pl4 ph_x
p2.6 pl5 ph2 phpdx0.1 phpdy0.2
""".split("\n")



def _check_allowed_parameters(out):

    assert set([v.name for v in PARAMS.values()]) == set(out.keys())


def test_parse_base_1():
    out = parse_base(test_string[0])

    _check_allowed_parameters(out)
    assert out["plen"] == 1.0
    assert out["power"] == 1.0
    assert out["phase"] == "1"
    assert out["channel"] == 2.0
    assert out["time"] is None


def test_parse_base_2():
    out = parse_base(test_string[1])

    _check_allowed_parameters(out)
    assert out["plen"] is None
    assert out["power"] is None
    assert out["text"] == r"$\\tau$"
    assert out["time"] == 1.0


def test_parse_base_3():
    out = parse_base(test_string[2])

    _check_allowed_parameters(out)
    assert out["plen"] is None
    assert out["time"] == 1.0
    assert out["channel"] == 1
    assert out["text"] == "TEST"
    assert out["text_dx"] == 0.1
    assert out["text_dy"] == 0.3
    

def test_parse_base_4():
    out = parse_base(test_string[4])

    _check_allowed_parameters(out)
    assert out["plen"] == 3.0
    assert out["power"] == 4.0
    assert out["phase"] == "_x"



def test_shape():
    seq = "p1 pl1 ph1 sp0 ch1"
    out = parse_base(seq, {"sp0": lambda x: x**2})
    assert callable(out["shape"]) 


def test_userparams():
    seq = "pH90 plH90 ph1 sp0 chH"
    upars = {
            "pH90": 1,
            "plH90": 2,
            "sp0": lambda x: x+1,
            "chH": 0,
        }
    out = parse_base(seq, params=upars)
    assert out["plen"] == 1.0
    assert out["power"] == 2.0
    assert callable(out["shape"])
    assert out["shape"](100) == 101
    assert out["channel"] == 0.0
    

if __name__ == "__main__":
    
    print(test_string[0])
