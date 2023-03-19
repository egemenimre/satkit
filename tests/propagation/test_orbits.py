# satkit: Satellite Mission Analysis and Design for Python
#
# Copyright (C) 2023 Egemen Imre
#
# Licensed under GNU GPL v3.0. See LICENSE.rst for more info.
"""
Test orbit related utilities, classes and methods.

"""
import pytest
from org.orekit.bodies import CelestialBodyFactory
from org.orekit.time import TimeScalesFactory
from org.orekit.utils import PVCoordinatesProvider

from satkit.propagation.orbits import generate_ephemeris_prop
from satkit.time.time import AbsoluteDateExt
from satkit.time.timeinterval import TimeInterval


def test_zero_stepsize_ephemeris():
    """Test `init` with zero stepsize - should raise `ZeroDivisionError`."""
    with pytest.raises(ZeroDivisionError):
        stepsize = 0.0  # seconds

        # shorthand for UTC
        utc = TimeScalesFactory.getUTC()

        sun_coords = PVCoordinatesProvider.cast_(CelestialBodyFactory.getSun())

        search_interval = TimeInterval(
            AbsoluteDateExt("2014-01-01T23:30:00.000", utc),
            AbsoluteDateExt("2014-01-01T23:35:00.000", utc),
        )

        generate_ephemeris_prop(search_interval, sun_coords, stepsize=stepsize)
