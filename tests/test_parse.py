from pulseplot import *

def test_parse_base_1():
    seq = r"p1 pl1 ph1 ch2"
    out = parse_base(seq)
    
    for k, v in PARAMS.items():
        assert v[0] in out.keys()

    assert out["plen"] == 1.0
    assert out["power"] == 1.0
    assert out["phase"] == "1"
    assert out["channel"] == 2.0
    assert out["time"] is None


def test_parse_base_2():
    seq = r"d1 ch1 tx$\\tau$"
    out = parse_base(seq)
    
    for k, v in PARAMS.items():
        assert v[0] in out.keys()

    assert out["plen"] is None
    assert out["power"] is None
    assert out["text"] == r"$\\tau$"


def test_parse_single():
    seq = r"ph2 tx2 ch2"
    out = parse_base(seq)
    assert out["phase"] == "2"
    assert out["text"] == "2"
    assert out["channel"] == 2.0


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
    assert out["channel"] == 0.0
    

if __name__ == "__main__":
    test_shape()
