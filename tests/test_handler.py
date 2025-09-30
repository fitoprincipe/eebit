"""Test for main class BitHandler."""

from eebit.bithandler import BitHandler


class TestBitHandler:
    def test_all_bits(self, l89_qa_bits, data_regression):
        bh = BitHandler(l89_qa_bits)
        data_regression.check(bh)

    def test_from_asset(self):
        handler = BitHandler.from_asset("LANDSAT/LC09/C02/T1_L2", "QA_PIXEL")
        print()
