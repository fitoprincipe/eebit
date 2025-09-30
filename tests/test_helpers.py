import pytest

from eebit import helpers


def test_format_bandname():
    """Test function format_bandname."""
    pass


class TestFormatBits:
    @pytest.mark.parametrize(
        "key, expected",
        [
            ("1-classname", "1-1-classname"),
        ],
    )
    def test_format_bit_key_valid(self, key, expected):
        """Test format_bit_key function with valid keys."""
        assert helpers.format_bit_key(key) == expected

    @pytest.mark.parametrize("key", ["a", "a-1", "1-1", "2-1-classname", "1_", "-1", "1-", ""])
    def test_format_bit_key_invalid(self, key):
        """Test that format_bit_key raises an error for invalid input."""
        with pytest.raises(ValueError):  # Replace ValueError with the actual expected exception
            helpers.format_bit_key(key)

    @pytest.mark.parametrize(
        "bit_info",
        [
            {"1-1-classname": {"0": "cat1", "2": "cat2"}},  # invalid position 2
            {"1-1-classname": {"cat0": 0, "cat1": 1}},  # invalid position cat0
            {"1-1-classname": {"0": "", "1": "cat2"}},  # empty string value
            {"1-1-classname": 123},  # invalid type
        ],
    )
    def test_format_bit_value_invalid(self, bit_info):
        """Test that format_bit_value raises an error for invalid input."""
        with pytest.raises(ValueError):  # Replace ValueError with the actual expected exception
            helpers.format_bits_info(bit_info)

    @pytest.mark.parametrize(
        "bit_info, expected",
        [
            (
                {"1-1-classname": "category"},
                {"1-1-classname": {"0": "no category", "1": "category"}},
            ),
            ({"2-classname": {"1": "cat1"}}, {"2-2-classname": {"1": "cat1"}}),
            (
                {"3-4-classname": {0: "cat1", 1: "cat2", 2: "cat3", 3: "cat4"}},
                {"3-4-classname": {"0": "cat1", "1": "cat2", "2": "cat3", "3": "cat4"}},
            ),
        ],
    )
    def test_format_bit_value_valid(self, bit_info, expected):
        """Test format_bit_value function with valid inputs."""
        assert helpers.format_bits_info(bit_info) == expected
