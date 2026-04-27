
import pytest
from pulseplot.parse import Pulse, Delay, PulseSeq, ParseError

def test_pulse_valid():
    p = Pulse("p=1 pl=2")
    assert p.plen == 1
    assert p.power == 2

def test_delay_valid():
    d = Delay("d=1")
    assert d.time == 1

def test_pulse_invalid_combination():
    with pytest.raises(ValueError, match="combination of a Pulse and a Delay"):
        Pulse("p=1 d=1")

def test_delay_invalid_combination():
    with pytest.raises(ValueError, match="combination of a Pulse and a Delay"):
        Delay("p=1 d=1")

def test_casting_error():
    with pytest.raises(ParseError, match="Cannot cast"):
        Pulse("p=abc")

def test_unknown_parameter():
    with pytest.raises(ParseError, match="Unknown sequence"):
        Pulse("p=1 unknown=2")

def test_malformed_parameter():
    # "p= 1" will fail because of the space. 
    # The regex \bp=?[^lhdkf ]+ expects no space after =
    with pytest.raises(ParseError):
        Pulse("p= 1")

def test_pulse_seq_invalid():
    # Now PulseSeq should preserve ParseError or raise ValueError if it's a combination issue
    with pytest.raises(ValueError):
        PulseSeq("p=1 d=1")

def test_whitespace_handling():
    # Should not raise errors
    Pulse("p=1  ")
    Pulse("  p=1")
    Pulse(" p=1   pl=2 ")

def test_no_space_between_params():
    # "p=1pl=2" should fail because p=1pl=2 is not a valid float
    with pytest.raises(ParseError):
        Pulse("p=1pl=2")

def test_multiple_unknowns():
    with pytest.raises(ParseError, match="Unknown sequence"):
        Pulse("p=1  u=2  d=1")

if __name__ == "__main__":
    pytest.main([__file__])
