# satkit: Satellite Mission Analysis and Design for Python
#
# Copyright (C) 2022 Egemen Imre
#
# Licensed under GNU GPL v3.0. See LICENSE.rst for more info.
"""
TLE class tests.

"""
from pathlib import Path

import pytest
from orekit.pyhelpers import setup_orekit_curdir
from org.orekit.bodies import OneAxisEllipsoid
from org.orekit.frames import FramesFactory
from org.orekit.propagation.analytical.tle import TLE, TLEPropagator
from org.orekit.time import AbsoluteDate, TimeScalesFactory
from org.orekit.utils import Constants, IERSConventions
from pytest import approx

from satkit import process_paths, u
from satkit.propagation.tle import TleFactory, TLEUtils

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
    # TURKSAT 4A
    line1 = "1 39522U 14007A   20162.50918981  .00000000  00000-0  00000-0 0  9995"
    line2 = "2 39522   0.0000 124.6158 0000000   0.0000   0.0000  1.00273791 23487"
    return line1, line2


@pytest.fixture
def tle_sso_lines():
    """Test Fixture with TLE for SSO repeat groundtrack."""
    # SENTINEL 2A
    line1 = "1 40697U 15028A   20164.50828565  .00000010  00000-0  20594-4 0  9999"
    line2 = "2 40697  98.5692 238.8182 0001206  86.9662 273.1664 14.30818200259759"

    return line1, line2


@pytest.fixture
def tle_geo(tle_geo_lines):
    """Generates the GEO TLE test setup."""
    return TLE(tle_geo_lines[0], tle_geo_lines[1])


@pytest.fixture
def tle_sso(tle_sso_lines):
    """Generates the TLE with SSO repeat groundtrack test setup."""
    return TLE(tle_sso_lines[0], tle_sso_lines[1])


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


def test_init_sso(tle_sso):
    """Test init Sun-synchronous satellite."""

    epoch = tle_sso.getDate()

    # sma and altitude in meters
    sma = TLEUtils.compute_sma(tle_sso)
    alt = sma - Constants.WGS84_EARTH_EQUATORIAL_RADIUS * u.m

    # Sentinel-2A has an LTAN of 22:30
    ltan = 22.5

    tle = TleFactory.init_sso(
        epoch,
        alt,
        ltan,
        eccentricity=tle_sso.getE(),
        arg_perigee=tle_sso.getPerigeeArgument(),
        mean_anomaly=tle_sso.getMeanAnomaly(),
        bstar=tle_sso.getBStar(),
        launch_year=tle_sso.getLaunchYear(),
        launch_nr=tle_sso.getLaunchNumber(),
        launch_piece=tle_sso.getLaunchPiece(),
        sat_num=tle_sso.getSatelliteNumber(),
        classification=tle_sso.getClassification(),
        rev_nr=tle_sso.getRevolutionNumberAtEpoch(),
        el_nr=tle_sso.getElementNumber(),
    )

    print("")
    print(tle_sso)
    print(tle)

    # print(tle_sso.node_rotation_rate())
    # print(tle.node_rotation_rate())

    # print((tle_sso.getRaan() * u.rad).to("deg"))
    # print((tle.getRaan() * u.rad).to("deg"))

    assert TLEUtils.compute_sma(tle).m_as("m") == approx(
        TLEUtils.compute_sma(tle_sso).m_as("m"), abs=(5e-5 * u.mm).m_as("m")
    )
    assert tle.getI() == approx(tle_sso.getI(), abs=(8e-5 * u.deg).m_as("rad"))

    assert tle.getRaan() == approx(tle_sso.getRaan(), abs=(0.045 * u.deg).m_as("rad"))
