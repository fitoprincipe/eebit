"""Test the bitmask module."""

import ee
import pytest

from eebit.bitmask import Bit, BitGroup, BitMask


class TestBit:
    """Test the Bit class."""

    def test_bit_initialization(self):
        """Test the initialization of a Bit object."""
        bit = Bit(position=3, positive="clouds")
        assert bit.position == 3
        assert bit.positive == "clouds"
        assert bit.negative == "no clouds"
        assert bit.value_map == {"0": "no clouds", "1": "clouds"}

    def test_bit_min_max_value(self):
        """Test the min_value and max_value properties of a Bit object."""
        bit = Bit(position=2, positive="water", negative="land")
        assert bit.min_value == int("100", 2)  # 4 in decimal
        assert bit.max_value == int("111", 2)  # 7 in decimal

    def test_is_postive(self):
        """Test the is_positive method of a Bit object."""
        bit = Bit(position=2, positive="snow")
        assert bit.is_positive(int("100", 2))  # 4 in decimal
        assert not bit.is_positive(int("000", 2))  # 0 in decimal
        assert not bit.is_positive(int("010", 2))  # 2 in decimal
        assert bit.is_positive(int("1001110", 2))  # 78 in decimal
        assert not bit.is_positive(int("0001010", 2))  # 10 in decimal

    def test_is_negative(self):
        """Test the is_negative method of a Bit object."""
        bit = Bit(position=2, positive="cloudy", negative="clear")
        assert bit.is_negative(int("000", 2))  # 0 in decimal
        assert not bit.is_negative(int("100", 2))  # 4 in decimal
        assert bit.is_negative(int("010", 2))  # 2 in decimal
        assert not bit.is_negative(int("111", 2))  # 7 in decimal
        assert not bit.is_negative(int("1010100", 2))  # 84 in decimal
        assert bit.is_negative(int("1010010", 2))  # 82 in decimal


class TestBitGroup:
    """Test the BitGroup class."""

    def test_bitgroup_initialization(self):
        """Test the initialization of a BitGroup object."""
        value_map = {0: "no clouds", 1: "low clouds", 2: "medium clouds", 3: "high clouds"}
        bit_group = BitGroup(
            min_position=1, max_position=2, value_map=value_map, description="Cloud levels"
        )
        assert bit_group.min_position == 1
        assert bit_group.max_position == 2
        assert bit_group.value_map == value_map
        assert bit_group.description == "Cloud levels"

    # def test_bitgroup_masks(self):
    #     """Test the get_mask method of a BitGroup object."""
    #     value_map = {
    #         0: "no clouds",
    #         1: "low clouds",
    #         2: "medium clouds",
    #         3: "high clouds"
    #     }
    #     bit_group = BitGroup(min_position=1, max_position=2, value_map=value_map, description="Cloud levels")
    #     assert bit_group.get_mask_by_bit_description("no clouds") == int("000", 2)  # 0 in decimal
    #     assert bit_group.get_mask_by_bit_description("low clouds") == int("010", 2)  # 2 in decimal
    #     assert bit_group.get_mask_by_bit_description("medium clouds") == int("100", 2)  # 4 in decimal
    #     assert bit_group.get_mask_by_bit_description("high clouds") == int("110", 2)  # 6 in decimal
    #     with pytest.raises(ValueError):
    #         bit_group.get_mask_by_bit_description("unknown")

    def test_bitgroup_to_dict(self):
        """Test the to_dict method of a BitGroup object."""
        value_map = {0: "no clouds", 1: "low clouds", 2: "medium clouds", 3: "high clouds"}
        bit_group = BitGroup(
            min_position=1, max_position=2, value_map=value_map, description="Cloud levels"
        )
        expected_dict = {
            "1-2-Cloud levels": {
                "0": "no clouds",
                "1": "low clouds",
                "2": "medium clouds",
                "3": "high clouds",
            }
        }
        assert bit_group.to_dict() == expected_dict

    def test_bitgroup_bit_values(self):
        """Test the bit_values property of a BitGroup object."""
        value_map = {1: "low", 2: "medium", 3: "high"}
        bit_group = BitGroup(
            min_position=1, max_position=2, value_map=value_map, description="cloud level"
        )
        expected_values = ["cloud level - low", "cloud level - medium", "cloud level - high"]
        assert bit_group.bit_values == expected_values

    def test_bitgroup_is_positive(self):
        """Test the is_positive method of a BitGroup object."""
        value_map = {0: "no clouds", 1: "low clouds", 2: "medium clouds", 3: "high clouds"}
        bit_group = BitGroup(
            min_position=1, max_position=2, value_map=value_map, description="Cloud levels"
        )
        assert bit_group.is_positive_by_description(
            int("11011001", 2), "no clouds"
        )  # 217 in decimal
        assert bit_group.is_positive_by_description(
            int("11011000", 2), "no clouds"
        )  # 216 in decimal
        assert bit_group.is_positive_by_description(
            int("11011010", 2), "low clouds"
        )  # 218 in decimal
        assert bit_group.is_positive_by_description(
            int("11011011", 2), "low clouds"
        )  # 219 in decimal
        assert bit_group.is_positive_by_description(
            int("11011100", 2), "medium clouds"
        )  # 220 in decimal
        assert bit_group.is_positive_by_description(
            int("11011101", 2), "medium clouds"
        )  # 221 in decimal
        assert bit_group.is_positive_by_description(
            int("11011110", 2), "high clouds"
        )  # 222 in decimal
        assert bit_group.is_positive_by_description(
            int("11011111", 2), "high clouds"
        )  # 223 in decimal
        assert not bit_group.is_positive_by_description(
            int("11011001", 2), "low clouds"
        )  # 217 in decimal
        assert not bit_group.is_positive_by_description(
            int("11011000", 2), "low clouds"
        )  # 216 in decimal
        assert not bit_group.is_positive_by_description(
            int("11011001", 2), "medium clouds"
        )  # 217 in decimal
        assert not bit_group.is_positive_by_description(
            int("11011000", 2), "medium clouds"
        )  # 216 in decimal
        assert not bit_group.is_positive_by_description(
            int("11011001", 2), "high clouds"
        )  # 217 in decimal
        assert not bit_group.is_positive_by_description(
            int("11011000", 2), "high clouds"
        )  # 216 in decimal

    def test_is_positive_by_key(self):
        """Test the is_positive_by_key method of a BitGroup object."""
        value_map = {0: "no clouds", 1: "low clouds", 2: "medium clouds", 3: "high clouds"}
        bit_group = BitGroup(
            min_position=1, max_position=2, value_map=value_map, description="Cloud levels"
        )
        assert bit_group.is_positive_by_key(int("11011001", 2), "0")  # 217 in decimal
        assert bit_group.is_positive_by_key(int("11011000", 2), 0)  # 216 in decimal
        assert bit_group.is_positive_by_key(int("11011010", 2), "1")  # 218 in decimal
        assert bit_group.is_positive_by_key(int("11011011", 2), 1)  # 219 in decimal
        assert bit_group.is_positive_by_key(int("11011100", 2), "2")  # 220 in decimal
        assert bit_group.is_positive_by_key(int("11011101", 2), 2)  # 221 in decimal
        assert bit_group.is_positive_by_key(int("11011110", 2), "3")  # 222 in decimal
        assert bit_group.is_positive_by_key(int("11011111", 2), 3)  # 223 in decimal
        assert not bit_group.is_positive_by_key(int("11011001", 2), "1")  # 217 in decimal
        assert not bit_group.is_positive_by_key(int("11011000", 2), 1)  # 216 in decimal
        assert not bit_group.is_positive_by_key(int("11011001", 2), "2")  # 217 in decimal
        assert not bit_group.is_positive_by_key(int("11011000", 2), 2)  # 216 in decimal
        assert not bit_group.is_positive_by_key(int("11011001", 2), "3")  # 217 in decimal
        assert not bit_group.is_positive_by_key(int("11011000", 2), 3)  # 216 in decimal

    def test_bitgroup_decode_value(self):
        """Test the decode_value method of a BitGroup object."""
        value_map = {0: "no clouds", 1: "low clouds", 2: "medium clouds", 3: "high clouds"}
        bit_group = BitGroup(
            min_position=1, max_position=2, value_map=value_map, description="Cloud levels"
        )
        assert bit_group.decode_value(int("000", 2)) == "no clouds"  # 0 in decimal
        assert bit_group.decode_value(int("010", 2)) == "low clouds"  # 2 in decimal
        assert bit_group.decode_value(int("100", 2)) == "medium clouds"  # 4 in decimal
        assert bit_group.decode_value(int("110", 2)) == "high clouds"  # 6 in decimal

    def test_bitgroup_incomplete_decode_value(self):
        """Test that BitGroup raises an error for incomplete value_map."""
        incomplete = BitGroup(
            min_position=1,
            max_position=2,
            value_map={0: "no clouds", 2: "medium clouds"},
            description="Cloud levels",
        )
        assert incomplete.decode_value(int("000", 2)) == "no clouds"
        assert incomplete.decode_value(int("010", 2)) == None
        assert incomplete.decode_value(int("100", 2)) == "medium clouds"
        assert incomplete.decode_value(int("110", 2)) == None

    def test_bitgroup_get_mask_by_position(
        self, aoi_patagonia, cloudy_l8_patagonia, ee_image_regression
    ):
        """Test the get_mask_by_position method of a BitGroup object."""
        group_dict = {"8-9-Cloud": {"1": "Low", "2": "Medium", "3": "High"}}
        bit_group = BitGroup.from_dict(group_dict)
        mask = bit_group.get_mask_by_position(cloudy_l8_patagonia.select("QA_PIXEL"), 3)
        masked = cloudy_l8_patagonia.updateMask(mask)
        vis = {"bands": ["SR_B4", "SR_B3", "SR_B2"], "min": 5000, "max": 20000}
        ee_image_regression.check(masked, region=aoi_patagonia, viz_params=vis)

    def test_bitgroup_get_mask_by_bit_value(
        self, aoi_patagonia, cloudy_l8_patagonia, ee_image_regression
    ):
        """Test the get_mask_by_bit_value method of a BitGroup object."""
        group_dict = {"8-9-Cloud": {"1": "Low", "2": "Medium", "3": "High"}}
        bit_group = BitGroup.from_dict(group_dict)
        mask = bit_group.get_mask_by_bit_value(cloudy_l8_patagonia.select("QA_PIXEL"), "high")
        masked = cloudy_l8_patagonia.updateMask(mask)
        vis = {"bands": ["SR_B4", "SR_B3", "SR_B2"], "min": 5000, "max": 20000}
        ee_image_regression.check(masked, region=aoi_patagonia, viz_params=vis)

    def test_bitgroup_get_masks(self, aoi_patagonia, cloudy_l8_patagonia, ee_image_regression):
        """Test the get_masks method of a BitGroup object."""
        group_dict = {"8-9-Cloud": {"1": "Low", "2": "Medium", "3": "High"}}
        bit_group = BitGroup.from_dict(group_dict)
        masks = bit_group.get_masks(cloudy_l8_patagonia.select("QA_PIXEL"))
        vis = {"min": 0, "max": 1}
        ee_image_regression.check(masks, region=aoi_patagonia, viz_params=vis)

    def test_bitgroup_decode_to_columns(
        self, aoi_patagonia, cloudy_l8_patagonia, ee_feature_collection_regression
    ):
        """Test the decode_to_columns method of a BitGroup object."""
        group_dict = {"8-9-Cloud": {"1": "Low", "2": "Medium", "3": "High"}}
        bit_group = BitGroup.from_dict(group_dict)
        points = ee.FeatureCollection.randomPoints(aoi_patagonia, 10)
        table = cloudy_l8_patagonia.reduceRegions(
            collection=points, reducer=ee.Reducer.first(), scale=30
        )
        decoded = bit_group.decode_to_columns(table, "QA_PIXEL")
        ee_feature_collection_regression.check(decoded)


class TestBitMask:
    """Test the BitMask class."""

    TEST_BITS_OK = {
        "1": "shadow",
        "2-3-Clouds": {
            "0": "no clouds",
            "1": "low clouds",
            "2": "medium clouds",
            "3": "high clouds",
        },
        "4-Snow": "snow",
        "5-Water": "water",
    }

    TEST_BITS_FAIL = {
        "1": "shadow",
        "2-3-Clouds": {
            "0": "no clouds",
            "1": "low clouds",
            "2": "medium clouds",
            "3": "high clouds",
        },
        "3-Snow": "snow",  # duplicate bit 3
        "5-Water": "water",
    }

    TEST_BITS_FAIL2 = {
        "1": "shadow",
        "2-Clouds": {
            "0": "no clouds",
        },
    }

    TEST_BITS_FAIL3 = {"1": "shadow", "2-3-Clouds": {}}

    TEST_BITS_FAIL4 = {
        "1": "shadow",
        "2-3-Clouds": {"1": "low clouds", "2": "medium clouds", "4": "high clouds"},
    }

    def test_bitmask_initialization(self):
        """Test the initialization of a BitMask object."""
        bitmask = BitMask.from_dict(self.TEST_BITS_OK)
        assert isinstance(bitmask, BitMask)

    def test_bitmask_all_bits_duplicate(self):
        """Test that BitMask raises an error for duplicate bits."""
        with pytest.raises(ValueError):
            BitMask.from_dict(self.TEST_BITS_FAIL)

    def test_bitmask_no_positive(self):
        """Test that BitMask raises an error for missing positive values."""
        with pytest.raises(ValueError):
            BitMask.from_dict(self.TEST_BITS_FAIL2)

    def test_bitmask_empty_value_map(self):
        """Test that BitMask raises an error for empty value map."""
        with pytest.raises(ValueError):
            BitMask.from_dict(self.TEST_BITS_FAIL3)

    def test_bitmask_invalid_value_map(self):
        """Test that BitMask raises an error for invalid value map."""
        with pytest.raises(ValueError):
            BitMask.from_dict(self.TEST_BITS_FAIL4)

    def test_bitmask_to_dict(self):
        """Test the to_dict method of a BitMask object."""
        bitmask = BitMask.from_dict(self.TEST_BITS_OK)
        expected = {
            "1-1-shadow": {"0": "no shadow", "1": "shadow"},
            "2-3-Clouds": {
                "0": "no clouds",
                "1": "low clouds",
                "2": "medium clouds",
                "3": "high clouds",
            },
            "4-4-Snow": {"0": "no snow", "1": "snow"},
            "5-5-Water": {"0": "no water", "1": "water"},
        }
        assert bitmask.to_dict() == expected

    def test_bitmask_get_masks(
        self, aoi_patagonia, cloudy_l8_patagonia, l89_qa_bits, ee_image_regression
    ):
        """Test the get_masks method of a BitMask object."""
        bitmask = BitMask.from_dict(l89_qa_bits)
        masks = bitmask.get_masks(cloudy_l8_patagonia.select("QA_PIXEL"))
        bands = masks.bandNames().getInfo()
        expected_bands = [
            "Cloud - no Cloud",
            "Cloud - Cloud",
            "Cloud Shadow - no Cloud Shadow",
            "Cloud Shadow - Cloud Shadow",
            "Snow - no Snow",
            "Snow - Snow",
            "Water - no Water",
            "Water - Water",
            "Cloud Confidence - Clouds Low Prob",
            "Cloud Confidence - Clouds Medium Prob",
            "Cloud Confidence - Clouds High Prob",
            "Shadow Confidence - Shadow Low Prob",
            "Shadow Confidence - Shadow Medium Prob",
            "Shadow Confidence - Shadow High Prob",
        ]
        assert bands == expected_bands
        test_image = masks.select(["Cloud - Cloud", "Cloud Shadow - Cloud Shadow", "Water - Water"])
        vis = {"min": 0, "max": 1}
        ee_image_regression.check(test_image, region=aoi_patagonia, viz_params=vis)

    def test_bitmask_decode_value(self):
        """Test the decode_value method of a BitMask object."""
        bitmask = BitMask.from_dict(self.TEST_BITS_OK)
        assert bitmask.decode_value(int("00000", 2)) == {
            "shadow": "no shadow",
            "clouds": "no clouds",
            "snow": "no snow",
            "water": "no water",
        }
        assert bitmask.decode_value(int("00010", 2)) == {
            "shadow": "no shadow",
            "Clouds": "low clouds",
            "Snow": "no snow",
            "Water": "no water",
        }
        assert bitmask.decode_value(int("00110", 2)) == {
            "shadow": "no shadow",
            "Clouds": "medium clouds",
            "Snow": "snow",
            "Water": "no water",
        }
        assert bitmask.decode_value(int("11111", 2)) == {
            "shadow": "shadow",
            "Clouds": "high clouds",
            "Snow": "snow",
            "Water": "water",
        }

    def test_bitmask_decode_to_columns(
        self, aoi_patagonia, cloudy_l8_patagonia, l89_qa_bits, ee_feature_collection_regression
    ):
        """Test the decode_to_columns method of a BitMask object."""
        bitmask = BitMask.from_dict(l89_qa_bits)
        points = ee.FeatureCollection.randomPoints(aoi_patagonia, 10)
        table = cloudy_l8_patagonia.reduceRegions(
            collection=points, reducer=ee.Reducer.first(), scale=30
        )
        decoded = bitmask.decode_to_columns(table, "QA_PIXEL")
        ee_feature_collection_regression.check(decoded)
