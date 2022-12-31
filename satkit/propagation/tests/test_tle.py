# satkit: Satellite Mission Analysis and Design for Python
#
# Copyright (C) 2022 Egemen Imre
#
# Licensed under GNU GPL v3.0. See LICENSE.rst for more info.
"""
TLE class tests.

"""
import pytest
import orekit
from pytest import approx
from orekit.pyhelpers import setup_orekit_curdir
from pathlib import Path

from org.orekit.bodies import OneAxisEllipsoid
from org.orekit.frames import FramesFactory
from org.orekit.propagation.analytical.tle import TLE, TLEPropagator
from org.orekit.time import AbsoluteDate, TimeScalesFactory
from org.orekit.utils import IERSConventions, Constants

from satkit import u, process_paths
from satkit.propagation.tle import TleFactory

extra_path = Path(
    "..",
    "..",
    "..",
)

orekit_data_file_path = Path("data", "orekit-data", "orekit-data-reference.zip")


def setup_module():
    """setup any state specific to the execution of the module."""

    #  Init Orekit data
    data_file = process_paths(orekit_data_file_path).resolve()

    setup_orekit_curdir(str(data_file))


@pytest.fixture
def tle_geo_lines():
    """Test Fixture with GEO TLE."""
    line1 = "1 39522U 14007A   20162.50918981  .00000000  00000-0  00000-0 0  9995"
    line2 = "2 39522   0.0000 124.6158 0000000   0.0000   0.0000  1.00273791 23487"
    return line1, line2


@pytest.fixture
def tle_geo(tle_geo_lines):
    """Generates the GEO TLE test setup."""
    return TLE(tle_geo_lines[0], tle_geo_lines[1])


def test_init_geo(tle_geo):
    """Test init GEO satellite.

    Check for longitude and the resulting TLE.
    """

    epoch = AbsoluteDate(2020, 6, 10, 12, 13, 14.0, TimeScalesFactory.getUTC())
    longitude = 42.0 * u.deg

    tle = TleFactory.init_geo(
        epoch,
        longitude,
        launch_year=2014,
        launch_piece="A",
        launch_nr=7,
        sat_num=39522,
        classification="U",
        rev_nr=2348,
        el_nr=999,
    )

    # print("")
    # print(tle)

    #  prepare the itrs frame and the Earth
    itrs = FramesFactory.getITRF(IERSConventions.IERS_2010, False)
    earth = OneAxisEllipsoid(
        Constants.WGS84_EARTH_EQUATORIAL_RADIUS, Constants.WGS84_EARTH_FLATTENING, itrs
    )
    # Get ITRS coordinate at initial time
    propagator = TLEPropagator.selectExtrapolator(tle)
    pvt = propagator.getPVCoordinates(epoch, itrs)

    #  Get lla at init time - should sit on the correct longitude
    lla = earth.transform(pvt.getPosition(), earth.getBodyFrame(), pvt.getDate())

    # print((lla.getLongitude() * u.rad).to("degrees"))

    assert longitude == approx(lla.getLongitude(), abs=5e-3 * u.deg)
    assert str(tle_geo) == str(tle)
