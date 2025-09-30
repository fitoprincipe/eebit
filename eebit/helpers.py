"""Helper functions."""

BANNED_BAND_CHAR = list(".*?[]{}+$^+()|")


def format_bandname(name: str, replacement: str = "_") -> str:
    """Format a band name to be allowed in GEE."""
    return str([name.replace(char, replacement) for char in BANNED_BAND_CHAR][0])


def is_int(value: str | int) -> bool:
    """Check if a string can be converted to an integer."""
    try:
        int(value)
    except ValueError:
        return False
    return True


def is_str(value: str) -> bool:
    """Check if a value is a string."""
    return not is_int(value) and len(value) > 0


def format_bit_key(bit: str) -> str:
    """Format a bit key."""
    parts = str(bit).split("-", 2)
    if len(parts) == 1:
        raise ValueError(f"Bad format for '{bit}'. Use 'start-end-catname'")
    if len(parts) == 2:
        if is_int(parts[0]) and is_str(parts[1]):
            parts = [parts[0], parts[0], parts[1]]
        else:
            raise ValueError(f"Bad format for '{bit}'. Use 'start-end-catname'")
    if len(parts) == 3:
        if is_int(parts[0]) and is_int(parts[1]) and parts[0] > parts[1]:
            raise ValueError(f"In bit {bit}, start bit must be less than or equal to end bit.")
        if not is_int(parts[0]) or not is_int(parts[1]):
            raise ValueError(f"Bad format for '{bit}'. Use 'start-end-catname'")
    return "-".join(parts)


def format_bit_value(value: str | dict) -> dict:
    """Format a bit value."""
    if isinstance(value, str):
        # assume 0 is the opposite of 1
        # return {"0": f"no {value}", "1": value}
        return {"1": value}
    elif isinstance(value, dict):
        formatted_value = {}
        for pos, val in value.items():
            if not is_int(pos):
                raise ValueError(f"Bit position '{pos}' must be an integer.")
            if not is_str(val):
                raise ValueError(f"Bit value '{val}' must be a non-empty string.")
            formatted_value[str(int(pos))] = val
        return formatted_value
    else:
        raise ValueError(f"Bit value must be a string or a dict, found {type(value)}.")


def format_bits_info(bits_info: dict) -> dict:
    """Format the bits information to match the expected.

    Expected bit class format:
    {
      "1-1-catname": "category",  # option 1, one category
      "2-2-catname": {
        "0": "cat1",
        "1": "cat2"
      },  # option 2, 2 or more bits.
      "3-4-catname": {
        "0": "cat1",
        "1": "cat2",
        "2": "cat3",
        "3": "cat4"
      }  # option 2, 2 or more bits.
    }

    Args:
        bits_info: the bits information.

    Example:
        .. code-block:: python

            from geetools.utils import format_bitmask

            bitmask = {
                '0-shadows condition': 'shadows',
                '1-2-cloud conditions': {
                    '0': 'no clouds',
                    '1': 'high clouds',
                    '2': 'mid clouds',
                    '3': 'low clouds'
                }
            }
            bitmask = format_bitmask(bitmask)
    """
    final_bit_info = {}
    classes = []

    for bit, info in bits_info.items():
        parts = str(bit).split("-", 2)
        if len(parts) == 1 and is_int(parts[0]):
            # when one bit is provided without description, use info to get description
            if isinstance(info, dict) and len(info) <= 2:
                bit_1 = info.get("1", info.get(1))
                if bit_1 is None:
                    raise ValueError(
                        f"For single bit the positive value must be set. Found: {info}"
                    )
                bit = f"{parts[0]}-{parts[0]}-{bit_1}"
            elif isinstance(info, str):
                bit = f"{parts[0]}-{parts[0]}-{info}"
            else:
                raise ValueError(f"For single bit the positive value must be set. Found: {info}")
        bit = format_bit_key(bit)
        start, end, catname = bit.split("-", 2)
        start, end = int(start), int(end)
        nbits = end - start + 1
        if nbits < 1:
            raise ValueError(f"In bit {bit}, start bit must be less than or equal to end bit.")
        if catname in classes:
            raise ValueError(
                f"Bits information cannot contain duplicated names. '{catname}' is duplicated."
            )
        classes.append(catname)
        if not isinstance(info, (str, dict)):
            raise ValueError(f"Bit value must be a string or a dict, found {type(info)}.")
        formatted_info = format_bit_value(info)
        if len(formatted_info) > 2**nbits:
            raise ValueError(
                f"Number of values in bit '{bit}' exceeds the number of bits ({nbits})."
            )
        positions = [int(pos) for pos in formatted_info.keys()]
        if any(pos >= 2**nbits for pos in positions):
            raise ValueError(
                f"One or more positions in bit '{bit}' are out of range for the number of bits ({nbits})."
            )
        final_bit_info[bit] = formatted_info
    return final_bit_info
