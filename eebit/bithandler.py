"""bit handler."""

import ee
import geestac

from eebit import helpers


class BitHandler:
    """Bit handler."""

    def __init__(self, bits: dict, bit_length: int | None = None):
        """Bit handler.

        Read / decode / write bits information encoded in Google Earth Engine images.

        Args:
            bits (dict): a dictionary containing the bits information in the following format:

            {
              "1-catname": "category",  # option 1, one category
              "2-3-catname": {
                "1": "cat1",
                "2": "cat2",
                "3": "cat3",
                "4": "cat4"
              }  # option 2, 2 or more bits.

            where "catname" is the name of the whole category represented by the group of bits

            Example (Landsat 9 QA_PIXEL band: https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC09_C02_T1_L2#bands)

            bits = {
              "3-Cloud": "Cloud",
              "4-Cloud Shadow": "Cloud Shadow",
              "5": "Snow",
              "7": "Water",
              "8-9": {
                "1": "Clouds Low Prob",
                "2": "Clouds Medium Prob",
                "3": "Clouds High Prob"
              },
              "10-11":  {
                "1": "Shadow Low Prob",
                "2": "Shadow Medium Prob",
                "3": "Shadow High Prob"
              }
            }

            bit_length: the length of the
        """
        self.bits = helpers.format_bits_info(bits)
        self._all_bits = None
        self.bit_length = (
            len(range(min(self.all_bits), max(self.all_bits) + 1)) if not bit_length else bit_length
        )

    @property
    def all_bits(self) -> list:
        """List of all bits."""
        if self._all_bits is None:
            allbits = []
            for key in self.bits.keys():
                decoded = helpers.decode_key(key)
                for bit in decoded:
                    if bit in allbits:
                        raise ValueError(f"bit {bit} is duplicated!")
                    allbits.append(bit)
            self._all_bits = allbits
        return self._all_bits

    def decode_image(self, image: ee.Image, band: int | str = 0) -> ee.Image:
        """Decode a bit band of an ee.Image.

        The band of the image must correspond to the bits of the BitHandler object.

        Args:
            image: the image that contains the band to decode.
            band (optional): the bit band. If None it uses the first band of the image.

        Returns:
            A new image with one band per class. The image properties ara NOT passed to the new image.
        """
        to_decode = image.select([band])
        masks = []
        for positions, values in self.bits.items():
            start, end = positions.split("-")
            start, end = ee.Image(int(start)), ee.Image(int(end)).add(1)
            decoded = (
                to_decode.rightShift(end).leftShift(end).bitwiseXor(to_decode).rightShift(start)
            )
            for position, val in values.items():
                mask = ee.Image(int(position)).eq(decoded).rename(val)
                masks.append(mask)
        return ee.Image.geetools.fromList(masks)

    @classmethod
    def from_asset(cls, asset_id: str, band: str, bit_length: int | None = None) -> "BitHandler":
        """Create an instance of BitHandler using the bits information fetched with geestac."""
        stac = geestac.fromId(asset_id)
        bits_info = stac.bands[band].bitmask.to_dict()
        return cls(bits_info, bit_length)
