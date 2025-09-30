"""Pytest session configuration."""

import ee
import pytest
import pytest_gee


def pytest_configure() -> None:
    """Initialize earth engine according to the environment."""
    pytest_gee.init_ee_from_service_account()


@pytest.fixture()
def l89_qa_bits():
    return {
        "3-3-Cloud": "Cloud",
        "4-4-Cloud Shadow": "Cloud Shadow",
        "5-5-Snow": "Snow",
        "7-7-Water": "Water",
        "8-9-Cloud Confidence": {
            "1": "Clouds Low Prob",
            "2": "Clouds Medium Prob",
            "3": "Clouds High Prob",
        },
        "10-11-Shadow Confidence": {
            "1": "Shadow Low Prob",
            "2": "Shadow Medium Prob",
            "3": "Shadow High Prob",
        },
    }


@pytest.fixture()
def cloudy_l8_patagonia():
    """A cloudy L8 image in Patagonia."""
    return ee.Image("LANDSAT/LC08/C02/T1_L2/LC08_231090_20240107")


@pytest.fixture()
def aoi_patagonia():
    """An AOI in Patagonia."""
    return ee.Geometry.Polygon(
        [[[-71.72, -42.96], [-71.72, -43.18], [-71.39, -43.18], [-71.39, -42.96]]]
    )
