from pulseplot import *

def test_parse_base_1():
    seq = r"p1 pl1 ph1 ch2"
    out = parse_base(seq)
    print(out)
    
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
    out = parse_single(seq)
    print(out)


def test_shape():
    seq = "p1 pl1 ph1 sp0 ch1"

    print(parse_base(seq, {"sp0": lambda x:x**2}))

    # fig, ax = pplot()
    # ax.params = {"sp0": lambda x: x**2}

    # ax.pseq(seq)


    

if __name__ == "__main__":
    test_shape()
