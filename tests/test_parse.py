from pulseplot import PARAMS, Delay, Pulse, PulseSeq, parse_base

test_string = r"""p1 pl1 ph1 f2
d1 f1 tx$\\tau$
d1 f1 tx=TEST tdx0.1 tdy0.3
p1 pl1 ph1 f8 fcr ecg al0.33
p3 pl4 ph_x f0 tx`text with spaces`
p2.6 pl5 ph2 phpdx0.1 phpdy0.2
"""

test_string_splitted = test_string.split("\n")


def _check_allowed_parameters(out):

    assert set([v.name for v in PARAMS.values()]) == set(out.keys())


def test_parse_base_1():
    out = parse_base(test_string_splitted[0])

    _check_allowed_parameters(out)
    assert out["plen"] == 1.0
    assert out["power"] == 1.0
    assert out["phase"] == "1"
    assert out["channel"] == 2.0
    assert out["time"] is None

    pX = Pulse(test_string_splitted[0])
    assert pX.plen == 1.0
    assert pX.power == 1.0
    assert pX.channel == 2.0
    assert pX.phase_params()["y"] == 3.15
    assert pX.phase_params()["x"] - 0.494949494 < 1e-2

    pX * 2
    assert pX.plen == 2.0

    pX + 3
    assert pX.plen == 5.0

    pX ** 2
    assert pX.power == 2.0


def test_parse_base_2():
    out = parse_base(test_string_splitted[1])

    _check_allowed_parameters(out)
    assert out["plen"] is None
    assert out["power"] == 1.0
    assert out["text"] == r"$\\tau$"
    assert out["time"] == 1.0


def test_parse_base_3():
    out = parse_base(test_string_splitted[2])

    _check_allowed_parameters(out)
    assert out["plen"] is None
    assert out["time"] == 1.0
    assert out["channel"] == 1
    assert out["text"] == "TEST"
    assert out["text_dx"] == 0.1
    assert out["text_dy"] == 0.3


def test_parse_base_4():
    out = parse_base(test_string_splitted[4])

    _check_allowed_parameters(out)
    assert out["plen"] == 3.0
    assert out["power"] == 4.0
    assert out["phase"] == "_x"
    assert out["text"] == "`text with spaces`"

    p = Pulse(test_string_splitted[4])
    assert p.text == "text with spaces"


def test_shape():
    seq = "p1 pl1 ph1 sp0 ch1"
    out = parse_base(seq, {"sp0": lambda x: x ** 2})
    assert callable(out["shape"])


def test_userparams():
    seq = "pH90 plH90 ph1 sp0 fH"
    upars = {
        "pH90": 1,
        "plH90": 2,
        "sp0": lambda x: x + 1,
        "fH": 0,
    }
    out = parse_base(seq, params=upars)
    assert out["plen"] == 1.0
    assert out["power"] == 2.0
    assert callable(out["shape"])
    assert out["shape"](100) == 101
    assert out["channel"] == 0.0


def test_pulse_seq():

    pseq = PulseSeq(test_string)

    assert isinstance(pseq.elements[0], Pulse)
    assert isinstance(pseq.elements[1], Delay)
    assert isinstance(pseq.elements[2], Delay)
    assert isinstance(pseq.elements[3], Pulse)
    assert isinstance(pseq.elements[4], Pulse)
    assert isinstance(pseq.elements[5], Pulse)

    assert pseq.elements[0].text_kw == {}
    assert pseq.elements[1].label_params() == {
        "x": 0.494949494949495,
        "y": 1.5,
        "s": "$\\\\tau$",
        "ha": "center",
        "va": "center",
        "fontsize": 10,
    }


if __name__ == "__main__":
    test_parse_base_4()
