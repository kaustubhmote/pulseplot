import pytest

from pulseplot.parse import Delay, ParseError, Pulse, PulseSeq, parse_base


def test_valid_pulse_and_delay():
    pulse = Pulse("p=1 pl=2")
    delay = Delay("d=1")

    assert pulse.plen == 1
    assert pulse.power == 2
    assert delay.time == 1


def test_boolean_flags_are_parsed_as_complete_parameters():
    pulse = Pulse("p1 c w kc troff o")

    assert pulse.centered is True
    assert pulse.wait is True
    assert pulse.keep_centered is True
    assert pulse.truncate_off is True
    assert pulse.open is True


def test_unknown_parameter_has_an_exact_span():
    with pytest.raises(ParseError) as caught:
        Pulse("p=1  unknown=2")

    error = caught.value
    assert error.span == (5, 14)
    assert error.instructions == "p=1  unknown=2"
    assert "Unknown or malformed parameter 'unknown=2'" in str(error)
    assert "     ^^^^^^^^^" in str(error)


def test_malformed_parameter_does_not_get_skipped():
    with pytest.raises(ParseError) as caught:
        Pulse("p= 1")

    assert caught.value.span == (0, 2)
    assert "Unknown or malformed parameter 'p='" in str(caught.value)


def test_invalid_number_reports_parameter_and_value():
    with pytest.raises(ParseError) as caught:
        Pulse("p=abc")

    error = caught.value
    assert error.span == (0, 5)
    assert isinstance(error.__cause__, ValueError)
    assert "Invalid value 'abc' for parameter 'p'; expected float" in str(error)


def test_invalid_external_value_is_distinguished_from_inline_value():
    with pytest.raises(ParseError) as caught:
        Pulse("pH90", external_params={"pH90": "not-a-number"})

    assert caught.value.span == (0, 4)
    assert "Invalid external value 'not-a-number'" in str(caught.value)
    assert "parameter 'pH90'" in str(caught.value)


@pytest.mark.parametrize("parameter", ["pkw", "tkw", "skw"])
def test_invalid_dictionary_reports_its_parameter(parameter):
    instruction = f"p1 {parameter}={{bad}}"

    with pytest.raises(ParseError) as caught:
        Pulse(instruction)

    error = caught.value
    assert error.span == (3, len(instruction))
    assert isinstance(error.__cause__, ValueError)
    assert f"Invalid dictionary for parameter '{parameter}'" in str(error)


def test_dictionary_values_with_spaces_remain_supported():
    pulse = Pulse("p1 tkw={'color': 'red', 'fontsize': 12}")

    assert pulse.text_kw == {'color': 'red', 'fontsize': 12}


def test_pulse_and_delay_conflict_points_to_second_parameter():
    with pytest.raises(ParseError) as caught:
        Pulse("p1 pl2 d3")

    error = caught.value
    assert error.span == (7, 9)
    assert "A combination of a Pulse and a Delay is not allowed" in str(error)


@pytest.mark.parametrize(
    ("constructor", "instruction", "message"),
    [
        (Pulse, "d1", "A delay parameter is not allowed in a Pulse"),
        (Delay, "p1", "A pulse parameter is not allowed in a Delay"),
    ],
)
def test_direct_constructors_reject_the_other_element_type(
    constructor, instruction, message
):
    with pytest.raises(ParseError) as caught:
        constructor(instruction)

    assert caught.value.span == (0, 2)
    assert message in str(caught.value)


def test_parameters_must_be_separated_by_whitespace():
    with pytest.raises(ParseError) as caught:
        Pulse("p=1pl=2")

    assert caught.value.span == (0, 7)


def test_sequence_error_includes_physical_line_and_column():
    sequence = """\
# preparation
p1
  d=bad
"""

    with pytest.raises(ParseError) as caught:
        PulseSeq(sequence)

    error = caught.value
    assert error.line_number == 3
    assert error.span == (2, 7)
    assert str(error).startswith("Line 3, column 3:\n")


def test_sequence_list_error_includes_element_index():
    with pytest.raises(ParseError) as caught:
        PulseSeq(["p1", "d=bad"])

    error = caught.value
    assert error.element_index == 1
    assert str(error).startswith("Element 2, column 1:\n")


def test_sequence_requires_a_pulse_or_delay_parameter():
    with pytest.raises(ParseError) as caught:
        PulseSeq("pl1 ph1")

    assert "Expected a pulse ('p') or delay ('d') parameter" in str(caught.value)


def test_comments_and_blank_lines_do_not_change_line_numbers():
    sequence = "\n# comment\n\np1\nunknown=2"

    with pytest.raises(ParseError) as caught:
        PulseSeq(sequence)

    assert caught.value.line_number == 5


def test_tabbed_input_uses_a_visually_aligned_pointer():
    with pytest.raises(ParseError) as caught:
        parse_base("\tp=abc")

    rendered = str(caught.value).splitlines()
    assert rendered[0] == "        p=abc"
    assert rendered[1] == "        ^^^^^"
