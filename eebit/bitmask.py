"""Bitmask module."""

from typing import Literal

import ee
import geetools  # noqa: F401

from eebit import helpers


class Bit:
    """Class that represents a single bit."""

    def __init__(self, position: int | str, positive: str, negative: str | None = None):
        """Initialize a Bit.

        Args:
            position: position of the bit.
            positive: positive bit description.
            negative: negative bit description. If None, it uses "no {positive}".
        """
        if helpers.is_int(position):
            self.position = int(position)
        else:
            raise TypeError("Bit position must be an integer.")
        self.positive = positive
        self.negative = negative or f"no {positive}"

    @property
    def min_value(self) -> int:
        """Get the minimum value of the bit."""
        return 1 << self.position

    @property
    def max_value(self) -> int:
        """Get the maximum value of the bit."""
        return (1 << (self.position + 1)) - 1

    def positive_values(self, n_bits: int | None = None) -> list:
        """Get the positive values of the bit.

        Args:
            n_bits: number of bits to consider. If None, it uses the bit position + 1.
        """
        if n_bits is None:
            n_bits = self.position
        return [n for n in range(self.min_value, (1 << n_bits + 1)) if self.is_positive(n)]

    def negative_values(self, n_bits: int | None = None) -> list:
        """Get the negative values of the bit.

        Args:
            n_bits: number of bits to consider. If None, it uses the bit position + 1.
        """
        if n_bits is None:
            n_bits = self.position
        return [n for n in range(0, (1 << n_bits + 1)) if self.is_negative(n)]

    def is_positive(self, value: int) -> bool:
        """Check if a value is positive for this bit.

        Args:
            value: the value to check.

        Returns:
            True if the value is positive for this bit, False otherwise.
        """
        if not isinstance(value, int):
            raise TypeError("Value must be an integer.")
        return (value & self.min_value) != 0

    def is_negative(self, value: int) -> bool:
        """Check if a value is negative for this bit.

        Args:
            value: the value to check.

        Returns:
            True if the value is negative for this bit, False otherwise.
        """
        if not isinstance(value, int):
            raise TypeError("Value must be an integer.")
        return (value & self.min_value) == 0

    @property
    def value_map(self) -> dict[Literal["0", "1"], str]:
        """Get the value map of the bit."""
        return {"0": self.negative, "1": self.positive}

    def to_bit_group(self, description: str) -> "BitGroup":
        """Convert a Bit to a BitGroup.

        Args:
            description: description of the bit group.

        Returns:
            A BitGroup object.
        """
        return BitGroup(
            min_position=self.position,
            max_position=self.position,
            value_map={0: self.negative, 1: self.positive},
            description=description,
        )


class BitGroup:
    """Class that represents a bit group."""

    BAND_NAME_PATTERN = "{description} - {value}"

    def __init__(self, description: str, min_position: int, max_position: int, value_map: dict):
        """Initialize a bit group.

        Args:
            min_position: minimum position of the bit group.
            max_position: maximum position of the bit group.
            value_map: a dict with the bit positions as keys and the bit descriptions as values. {bit-key: bit-value}
            description: description of the bit group. Different from each bit descriptions in the value_map.
        """
        description = description.lower()  # normalize description to lowercase
        # validate min_position and max_position
        if not helpers.is_int(min_position) or not helpers.is_int(max_position):
            raise TypeError("Bit positions must be integers.")
        min_position, max_position = int(min_position), int(max_position)
        if min_position < 0 or max_position < 0:
            raise ValueError("Bit positions must be non-negative.")
        if min_position > max_position:
            raise ValueError("Minimum position must be less than or equal to maximum position.")
        self.min_position = min_position
        self.max_position = max_position
        self.description = description
        # number of alternative values
        self.n_values = 2 ** (max_position - min_position + 1)  # 2^n where n is the number of bits
        # validate value_map
        _value_map = {}
        for k, v in value_map.items():
            if not helpers.is_int(k):
                raise ValueError(f"Bit position '{k}' must be an integer.")
            if not helpers.is_str(v):
                raise ValueError(f"Bit value '{v}' must be a non-empty string.")
            k_int = int(k)
            if k_int in _value_map:
                raise ValueError(f"Bit position '{k}' is duplicated in the value map.")
            if k_int < 0 or k_int >= self.n_values:
                raise ValueError(
                    f"Bit position '{k}' is out of range for the bit group ({self.n_values} values)."
                )
            _value_map[k_int] = v.lower()  # normalize value to lowercase
        if len(_value_map) == 0:
            raise ValueError("Value map cannot be empty.")
        if (min_position == max_position) and (len(_value_map) == 1) and (1 not in _value_map):
            raise ValueError("For single bit groups, the value map must contain a value for bit 1.")
        self.value_map = _value_map
        self._reverse_value_map = {v: k for k, v in self.value_map.items()}

    def to_dict(self) -> dict:
        """Convert a bit group to a dict."""
        key = f"{self.min_position}-{self.max_position}-{self.description}"
        value = {str(k): v for k, v in self.value_map.items()}
        return {key: value}

    def _get_key_for_bit_value(self, value: str) -> int:
        """Get the key for a given bit value.

        Args:
            value: the bit value to get the key for.
        """
        key = self._reverse_value_map.get(value)
        if key is None:
            raise ValueError(
                f"Key for value '{value}' not found in the value map '{self.value_map}'."
            )
        return key

    def _get_value_for_bit_key(self, key: int) -> str:
        """Get the bit value for a given bit key."""
        value = self.value_map.get(key)
        if value is None:
            raise ValueError(f"Key '{key}' not found in the value map '{self.value_map}'.")
        return value

    # def get_mask_by_bit_key(self, key: int | str) -> int:
    #     """Get the mask for a given key.
    #
    #     Args:
    #         key: the key to get the mask for.
    #
    #     Returns:
    #         The mask for the given key.
    #     """
    #     if not helpers.is_int(key):
    #         raise TypeError("Bit key must be an integer.")
    #     key = int(key)
    #     if key < 0 or key >= self.n_values:
    #         raise ValueError(f"Bit key '{key}' is out of range for the bit group ({self.n_values} values).")
    #     # shift the key to the left by min_position
    #     return key << self.min_position
    #
    # def get_mask_by_bit_description(self, description: str) -> int:
    #     """Get the mask for a given description.
    #
    #     Args:
    #         description: the description to get the mask for.
    #
    #     Returns:
    #         The mask for the given description.
    #     """
    #     key = self._get_key_for_bit_description(description)
    #     # shift the key to the left by min_position
    #     return self.get_mask_by_bit_key(key)

    @property
    def group_mask(self) -> int:
        """Get the mask for the entire group."""
        num_bits = self.max_position - self.min_position + 1
        return (1 << num_bits) - 1

    def decode_value(self, value: int) -> str | None:
        """Decode a value into its description.

        Args:
            value: the value to decode.

        Returns:
            The description of the value, or None if not found.
        """
        group_value = (value >> self.min_position) & self.group_mask
        return self.value_map.get(group_value)

    def is_positive_by_key(self, value: int, key: int | str) -> bool:
        """Check if a value is positive for this key.

        Args:
            value: the value to check.
            key: the key to check.

        Returns:
            True if the value is positive for the passed key, False otherwise.
        """
        if not helpers.is_int(key):
            raise TypeError("Bit key must be an integer.")
        key = int(key)
        # if key < 0 or key >= self.n_values:
        if key not in self.value_map:
            raise ValueError(
                f"Bit key '{key}' is out of range for the bit group ({self.n_values} values)."
            )
        actual_group_value = (value >> self.min_position) & self.group_mask
        return actual_group_value == key

    def is_positive_by_key_gee(self, value: ee.Number, key: int | str) -> bool:
        """Check if a value is positive for this key using GEE.

        Args:
            value: the value to check.
            key: the key to check.

        Returns:
            True if the value is positive for the passed key, False otherwise.
        """
        if not helpers.is_int(key):
            raise TypeError("Bit key must be an integer.")
        key = int(key)
        # if key < 0 or key >= self.n_values:
        if key not in self.value_map:
            raise ValueError(
                f"Bit key '{key}' is out of range for the bit group ({self.n_values} values)."
            )
        actual_group_value = value.rightShift(self.min_position).bitwiseAnd(self.group_mask)
        return actual_group_value.eq(key)

    def is_positive_by_description(self, value: int, description: str) -> bool:
        """Check if a value is positive for this description.

        Args:
            value: the value to check.
            description: the description to check.

        Returns:
            True if the value is positive for the passed description, False otherwise.
        """
        ## Alternative implementation using get_mask
        # use get_mask to get the mask for the description
        # mask = self.get_mask(description)
        # rest = value >> (self.max_position + 1) << (self.max_position + 1)
        # value = (value - rest) >> self.min_position << self.min_position
        # return value == mask
        expected_group_value = self._get_key_for_bit_value(description)
        return self.is_positive_by_key(value, expected_group_value)

    def is_positive_by_description_gee(self, value: ee.Number, description: str) -> bool:
        """Check if a value is positive for this description using GEE.

        Args:
            value: the value to check.
            description: the description to check.

        Returns:
            True if the value is positive for the passed description, False otherwise.
        """
        expected_group_value = self._get_key_for_bit_value(description)
        return self.is_positive_by_key_gee(value, expected_group_value)

    def is_positive(
        self, value: int, key: int | str | None = None, description: str | None = None
    ) -> bool:
        """Check if a value is positive for this bit group.

        Args:
            value: the value to check.
            key: the key to check.
            description: the description to check.

        Returns:
            True if the value is positive for the passed key or description, False otherwise.
        """
        if key is not None and description is not None:
            raise ValueError("Only one of key or description should be provided.")
        if key is not None:
            return self.is_positive_by_key(value, key)
        elif description is not None:
            return self.is_positive_by_description(value, description)
        else:
            raise ValueError("Either key or description must be provided.")

    def is_positive_gee(
        self, value: ee.Number, key: int | str | None = None, description: str | None = None
    ) -> bool:
        """Check if a value is positive for this bit group using GEE.

        Args:
            value: the value to check.
            key: the key to check.
            description: the description to check.

        Returns:
            True if the value is positive for the passed key or description, False otherwise.
        """
        if key is not None and description is not None:
            raise ValueError("Only one of key or description should be provided.")
        if key is not None:
            return self.is_positive_by_key_gee(value, key)
        elif description is not None:
            return self.is_positive_by_description_gee(value, description)
        else:
            raise ValueError("Either key or description must be provided.")

    @property
    def bit_values(self) -> list[str]:
        """Get the list of bit values in the value map."""
        if self.min_position == self.max_position:
            if len(self.value_map) == 1:
                l = [self.description]
            else:
                if self.description == self.value_map[1]:
                    l = [self.description, self.value_map[0]]
                else:
                    l = [self.value_map[0], self.description]
        else:
            l = [
                self.BAND_NAME_PATTERN.format(description=self.description, value=v)
                for v in self.value_map.values()
            ]
        return l

    def get_mask_by_position(self, image: ee.Image, position: int | str) -> ee.Image:
        """Get a mask for a given bit position in the group.

        Args:
            image: the image to get the mask from.
            position: the position of the bit in the group.

        Returns:
            A binary image with 1 for pixels that have the bit set, and 0 otherwise.
        """
        if not helpers.is_int(position):
            raise TypeError("Bit position must be an integer.")
        position = int(position)
        decoded = image.rightShift(self.min_position).bitwiseAnd(self.group_mask)
        bname = self.BAND_NAME_PATTERN.format(
            description=self.description, value=self._get_value_for_bit_key(position)
        )
        return decoded.eq(position).rename(bname)

    def get_mask_by_bit_value(self, image: ee.Image, value: str) -> ee.Image:
        """Get a mask for a given bit value in the group.

        Args:
            image: the image to get the mask from.
            value: the bit value to get the mask for.

        Returns:
            A binary image with 1 for pixels that have the description, and 0 otherwise.
        """
        key = self._get_key_for_bit_value(value)
        # shift the image to the right by min_position
        shifted = image.rightShift(self.min_position)
        # get the bit at the given position
        bit = shifted.bitwiseAnd(self.group_mask)
        # return a binary image
        bname = self.BAND_NAME_PATTERN.format(description=self.description, value=value)
        return bit.eq(key).rename(bname)

    def get_masks(self, image: ee.Image) -> ee.Image:
        """Get masks for all bit values in the group.

        Args:
            image: the image to get the masks from.

        Returns:
            An image with one band per bit value in the group.
        """
        masks = []
        for key, value in self.value_map.items():
            mask = self.get_mask_by_bit_value(image, value)
            masks.append(mask)
        return ee.Image.geetools.fromList(masks)

    def decode_to_columns(self, table: ee.FeatureCollection, column: str) -> ee.FeatureCollection:
        """Decode a column in a FeatureCollection into multiple columns.

        Args:
            table: the FeatureCollection to decode.
            column: the column to decode.

        Returns:
            A new FeatureCollection with one column per bit value in the group.
        """
        for key, value in self.value_map.items():
            column_name = self.BAND_NAME_PATTERN.format(description=self.description, value=value)

            def set_bit_value(f: ee.Feature) -> ee.Feature:
                v = f.get(column)
                is_pos = self.is_positive_by_key_gee(ee.Number(v), key)
                return f.set(column_name, is_pos)

            table = table.map(set_bit_value)
        return table

    @classmethod
    def from_dict(cls, bit_info: dict) -> "BitGroup":
        """Create a BitGroup from a dict.

        Args:
            bit_info: a dict with the bit positions as keys and the bit descriptions as values.

        Returns:
            A BitGroup object.
        """
        if len(bit_info) != 1:
            raise ValueError("Bit info must contain exactly one entry.")
        key = list(bit_info.keys())[0]
        value = bit_info[key]
        start, end, description = key.split("-", 2)
        return cls(
            min_position=int(start),
            max_position=int(end),
            value_map={int(k): v for k, v in value.items()},
            description=description,
        )


class BitMask:
    """Class that represents a bit mask in a BitBand."""

    def __init__(self, bits: list[BitGroup], total: int | None = None):
        """Initialize a bitmask.

        Args:
            bits: a list of BitGroup.
            total: total number of bits. If None, it uses the maximum position of the last group + 1.
        """
        _bits = []
        _descriptions = []
        for bit in bits:
            group = bit.to_bit_group(description=bit.positive) if isinstance(bit, Bit) else bit
            if not isinstance(group, BitGroup):
                raise TypeError("Bits must be a list of Bit or BitGroup.")
            if group.description in _descriptions:
                raise ValueError(
                    f"Bit description '{group.description}' is duplicated in the bitmask."
                )
            _descriptions.append(group.description)
            _bits.append(group)
        # check for overlapping bits
        all_positions = []
        for group in _bits:
            positions = list(range(group.min_position, group.max_position + 1))
            for pos in positions:
                if pos in all_positions:
                    raise ValueError(f"Bit position {pos} is duplicated in the bitmask.")
                all_positions.append(pos)
        self.bits = _bits
        self.total = total or (self.bits[-1].max_position + 1)

    def to_dict(self) -> dict:
        """Convert a Bitmask into a dict."""
        final = {}
        for group in self.bits:
            final.update(group.to_dict())
        return final

    @classmethod
    def from_dict(cls, bits_info: dict) -> "BitMask":
        """Create a BitMask from a dict."""
        formatted = helpers.format_bits_info(bits_info)
        groups = []
        for key, value in formatted.items():
            start, end, description = key.split("-", 2)
            group = BitGroup(
                min_position=int(start),
                max_position=int(end),
                value_map={int(k): v for k, v in value.items()},
                description=description,
            )
            groups.append(group)
        return cls(bits=groups)

    def get_group_by_description(self, description: str) -> BitGroup:
        """Get the BitGroup that match a given description.

        Args:
            description: the description to search for.

        Returns:
            The BitGroup that match the given description.
        """
        bits = [bit for bit in self.bits if bit.description == description]
        if len(bits) == 0:
            raise ValueError(f"Description '{description}' not found in the bitmask.")
        return bits[0]

    def decode_value(self, value: int) -> dict[str, str | None]:
        """Decode a value into its descriptions.

        Args:
            value: the value to decode.

        Returns:
            A dict with the descriptions of the value, or None if not found.
        """
        decoded = {}
        for group in self.bits:
            decoded[group.description] = group.decode_value(value)
        return decoded

    def bit_values(self) -> list[str]:
        """Get the list of bit values in the bitmask."""
        values = []
        for group in self.bits:
            values.extend(group.bit_values)
        return values

    def get_masks(self, image: ee.Image) -> ee.Image:
        """Get masks for all bit values in the bitmask.

        Returns:
            An image with one band per bit value in the bitmask.
        """
        masks = []
        for group in self.bits:
            group_masks = group.get_masks(image)
            masks.append(group_masks)
        return ee.Image.geetools.fromList(masks)

    def decode_to_columns(self, table: ee.FeatureCollection, column: str) -> ee.FeatureCollection:
        """Decode a column in a FeatureCollection into multiple columns.

        Args:
            table: the FeatureCollection to decode.
            column: the column to decode.

        Returns:
            A new FeatureCollection with one column per bit value in the bitmask.
        """
        for group in self.bits:
            table = group.decode_to_columns(table, column)
        return table
