# satkit: Satellite Mission Analysis and Design for Python
#
# Copyright (C) 2023 Egemen Imre
#
# Licensed under GNU GPL v3.0. See LICENSE.rst for more info.
"""
Tests for ground-based event and interval finders.

"""
from math import radians

from org.hipparchus.geometry.euclidean.threed import Vector3D
from org.orekit.bodies import GeodeticPoint, OneAxisEllipsoid
from org.orekit.frames import FramesFactory
from org.orekit.orbits import KeplerianOrbit
from org.orekit.propagation.analytical import KeplerianPropagator
from org.orekit.time import TimeScalesFactory
from org.orekit.utils import Constants, IERSConventions, TimeStampedPVCoordinates

from satkit import u
from satkit.events.eventfinders import (
    StandardDawnDuskElevs,
    gnd_illum_finder,
    gnd_pass_finder,
    sat_illum_finder,
)
from satkit.time.time import AbsoluteDateExt
from satkit.time.timeinterval import TimeInterval


def earth():
    # Earth and frame
    itrf = FramesFactory.getITRF(IERSConventions.IERS_2010, True)
    planet_earth = OneAxisEllipsoid(
        Constants.WGS84_EARTH_EQUATORIAL_RADIUS, Constants.WGS84_EARTH_FLATTENING, itrf
    )
    return planet_earth


def kep_propagator():
    """Test Fixture with GEO TLE."""
    initialDate = AbsoluteDateExt("2014-01-01T23:30:00.000", TimeScalesFactory.getUTC())
    position = Vector3D(-6142438.668, 3492467.560, -25767.25680)
    velocity = Vector3D(505.8479685, 942.7809215, 7435.922231)
    pos_vel_time = TimeStampedPVCoordinates(initialDate, position, velocity)

    inertialFrame = FramesFactory.getEME2000()  # inertial frame for orbit definition
    initialOrbit = KeplerianOrbit(pos_vel_time, inertialFrame, Constants.WGS84_EARTH_MU)

    # Propagator : consider a simple keplerian motion (could be more elaborate)
    propagator = KeplerianPropagator(initialOrbit)

    return propagator


def gnd_location():
    longitude = radians(45.0)
    latitude = radians(25.0)
    altitude = 0
    gnd_pos = GeodeticPoint(latitude, longitude, float(altitude))

    return gnd_pos


def elev_event_inputs_outputs():
    """
    Elevation event/interval finder inputs and outputs.
    """
    # shorthand for UTC
    utc = TimeScalesFactory.getUTC()

    input_output_tuples = []

    # Nominal case
    nominal_search_interval = TimeInterval(
        AbsoluteDateExt("2014-01-01T23:30:00.000", utc),
        AbsoluteDateExt("2014-01-02T23:30:00.000", utc),
    )
    nominal_output = [
        TimeInterval(
            AbsoluteDateExt("2014-01-01T23:31:49.55286151707821Z", utc),
            AbsoluteDateExt("2014-01-01T23:42:49.64917646999244Z", utc),
        ),
        TimeInterval(
            AbsoluteDateExt("2014-01-02T01:11:23.26932478260755Z", utc),
            AbsoluteDateExt("2014-01-02T01:18:20.66899834602248Z", utc),
        ),
        TimeInterval(
            AbsoluteDateExt("2014-01-02T11:38:01.53899331924902Z", utc),
            AbsoluteDateExt("2014-01-02T11:48:04.87831264440055Z", utc),
        ),
        TimeInterval(
            AbsoluteDateExt("2014-01-02T13:15:29.16139702783088Z", utc),
            AbsoluteDateExt("2014-01-02T13:25:06.87081687644551Z", utc),
        ),
        TimeInterval(
            AbsoluteDateExt("2014-01-02T22:35:21.16795871369053Z", utc),
            AbsoluteDateExt("2014-01-02T22:41:52.24229878175758Z", utc),
        ),
    ]

    input_output_tuples.append((nominal_search_interval, nominal_output))

    # Search starts inside a pass
    begin_with_pass_search_interval = TimeInterval(
        AbsoluteDateExt("2014-01-01T23:35:00.000", utc),
        AbsoluteDateExt("2014-01-02T23:30:00.000", utc),
    )
    begin_with_pass_output = deep_copy_intervals(nominal_output)
    begin_with_pass_output[0] = TimeInterval(
        AbsoluteDateExt("2014-01-01T23:35:00.000", utc),
        AbsoluteDateExt("2014-01-01T23:42:49.64917646999244Z", utc),
    )

    input_output_tuples.append(
        (begin_with_pass_search_interval, begin_with_pass_output)
    )

    # Search ends inside a pass
    end_with_pass_search_interval = TimeInterval(
        AbsoluteDateExt("2014-01-01T23:30:00.000", utc),
        AbsoluteDateExt("2014-01-02T22:38:00.000", utc),
    )
    end_with_pass_output = deep_copy_intervals(nominal_output)
    end_with_pass_output[-1] = TimeInterval(
        AbsoluteDateExt("2014-01-02T22:35:21.16795871369053Z", utc),
        AbsoluteDateExt("2014-01-02T22:38:00.000", utc),
    )

    input_output_tuples.append((end_with_pass_search_interval, end_with_pass_output))

    # Search interval too short, but is inside a pass
    short_search_interval_1 = TimeInterval(
        AbsoluteDateExt("2014-01-01T23:35:00.000", utc),
        AbsoluteDateExt("2014-01-01T23:40:00.000", utc),
    )
    short_output_1 = [
        TimeInterval(
            AbsoluteDateExt("2014-01-01T23:35:00.000", utc),
            AbsoluteDateExt("2014-01-01T23:40:00.000", utc),
        )
    ]
    input_output_tuples.append((short_search_interval_1, short_output_1))

    # Search interval is outside passes - no pass to be found
    no_pass_search_interval = TimeInterval(
        AbsoluteDateExt("2014-01-02T20:35:00.000", utc),
        AbsoluteDateExt("2014-01-02T21:40:00.000", utc),
    )
    no_pass_output = []
    input_output_tuples.append((no_pass_search_interval, no_pass_output))

    return input_output_tuples


def gnd_illum_event_inputs_outputs():
    """
    Ground illumination event/interval finder inputs and outputs.
    """
    # shorthand for UTC
    utc = TimeScalesFactory.getUTC()

    input_output_tuples = []

    # Nominal case
    nominal_search_interval = TimeInterval(
        AbsoluteDateExt("2014-01-01T23:30:00.000", utc),
        AbsoluteDateExt("2014-01-03T23:55:00.000", utc),
    )
    nominal_output = [
        TimeInterval(
            AbsoluteDateExt("2014-01-02T03:20:23.78850932774926Z", utc),
            AbsoluteDateExt("2014-01-02T14:47:39.42716052571426Z", utc),
        ),
        TimeInterval(
            AbsoluteDateExt("2014-01-03T03:20:40.67633771842178Z", utc),
            AbsoluteDateExt("2014-01-03T14:48:18.72433753081995Z", utc),
        ),
    ]
    input_output_tuples.append((nominal_search_interval, nominal_output))

    # Search interval too short, but is inside a daytime
    short_search_interval_1 = TimeInterval(
        AbsoluteDateExt("2014-01-01T13:30:00.000", utc),
        AbsoluteDateExt("2014-01-01T13:40:00.000", utc),
    )
    short_output_1 = [
        TimeInterval(
            AbsoluteDateExt("2014-01-01T13:30:00.000", utc),
            AbsoluteDateExt("2014-01-01T13:40:00.000", utc),
        )
    ]
    input_output_tuples.append((short_search_interval_1, short_output_1))

    # Search interval is outside daytime - no interval to be found
    no_pass_search_interval = TimeInterval(
        AbsoluteDateExt("2014-01-01T23:30:00.000", utc),
        AbsoluteDateExt("2014-01-01T23:35:00.000", utc),
    )
    no_pass_output = []
    input_output_tuples.append((no_pass_search_interval, no_pass_output))

    return input_output_tuples


def sat_illum_event_inputs_outputs():
    """
    Satellite illumination event/interval finder inputs and outputs.
    """
    # shorthand for UTC
    utc = TimeScalesFactory.getUTC()

    input_output_tuples = []

    # Nominal case
    nominal_search_interval = TimeInterval(
        AbsoluteDateExt("2014-01-02T13:30:00.000", utc),
        AbsoluteDateExt("2014-01-02T19:55:00.000", utc),
    )
    nominal_output = [
        TimeInterval(
            AbsoluteDateExt("2014-01-02T13:30:00.000Z", utc),
            AbsoluteDateExt("2014-01-02T14:12:13.74241700170296Z", utc),
        ),
        TimeInterval(
            AbsoluteDateExt("2014-01-02T14:42:58.51370738587114Z", utc),
            AbsoluteDateExt("2014-01-02T15:50:47.59348409786843Z", utc),
        ),
        TimeInterval(
            AbsoluteDateExt("2014-01-02T16:21:33.30719495502429Z", utc),
            AbsoluteDateExt("2014-01-02T17:29:21.44711669260403Z", utc),
        ),
        TimeInterval(
            AbsoluteDateExt("2014-01-02T18:00:08.10071208569268Z", utc),
            AbsoluteDateExt("2014-01-02T19:07:55.30330915194212Z", utc),
        ),
        TimeInterval(
            AbsoluteDateExt("2014-01-02T19:38:42.89425732046966Z", utc),
            AbsoluteDateExt("2014-01-02T19:55:00.000Z", utc),
        ),
    ]
    input_output_tuples.append((nominal_search_interval, nominal_output))

    # Search interval too short, but is inside a daytime
    short_search_interval_1 = TimeInterval(
        AbsoluteDateExt("2014-01-02T13:30:00.000", utc),
        AbsoluteDateExt("2014-01-02T13:40:00.000", utc),
    )
    short_output_1 = [
        TimeInterval(
            AbsoluteDateExt("2014-01-02T13:30:00.000", utc),
            AbsoluteDateExt("2014-01-02T13:40:00.000", utc),
        )
    ]
    input_output_tuples.append((short_search_interval_1, short_output_1))

    # Search interval is outside daytime - no interval to be found
    no_pass_search_interval = TimeInterval(
        AbsoluteDateExt("2014-01-01T23:30:00.000", utc),
        AbsoluteDateExt("2014-01-01T23:35:00.000", utc),
    )
    no_pass_output = []
    input_output_tuples.append((no_pass_search_interval, no_pass_output))

    return input_output_tuples


def deep_copy_intervals(interval_list):
    return [TimeInterval.from_interval(interval) for interval in interval_list]


# we can't use pytest parametrize here, as elev_event_inputs_outputs() requires orekit to be initialised
# parametrize is called before orekit init, causing an exception
def test_elevation_events():
    # elevation definition
    elevation = 5 * u.deg

    # loop through each input - output couple
    for search_interval, expected_intervals in elev_event_inputs_outputs():
        # find passes
        passes = gnd_pass_finder(
            search_interval,
            gnd_location(),
            elevation,
            propagator=kep_propagator(),
            planet=earth(),
        )

        # make sure output and expected value are of the same length
        assert len(passes.intervals) == len(expected_intervals)

        # check each interval to ensure equality
        for interval, exp_interval in zip(passes.intervals, expected_intervals):
            # if not interval.is_equal(exp_interval):
            # print(interval)
            # print("--------")
            # print(exp_interval)
            # print("*********")

            assert interval.is_equal(exp_interval, tolerance=100 * u.ns)


# we can't use pytest parametrize here, as elev_event_inputs_outputs() requires orekit to be initialised
# parametrize is called before orekit init, causing an exception
def test_gnd_illum_events():
    # elevation definition
    elevation = StandardDawnDuskElevs.CIVIL_DAWN_DUSK_ELEVATION

    # loop through each input - output couple
    for search_interval, expected_intervals in gnd_illum_event_inputs_outputs():
        # find passes
        passes = gnd_illum_finder(
            search_interval, gnd_location(), elevation, planet=earth()
        )

        # make sure output and expected value are of the same length
        assert len(passes.intervals) == len(expected_intervals)

        # check each interval to ensure equality
        for interval, exp_interval in zip(passes.intervals, expected_intervals):
            # if not interval.is_equal(exp_interval):
            # print(interval)
            # print("--------")
            # print(exp_interval)
            # print("*********")

            assert interval.is_equal(exp_interval, tolerance=100 * u.ns)


# we can't use pytest parametrize here, as elev_event_inputs_outputs() requires orekit to be initialised
# parametrize is called before orekit init, causing an exception
def test_sat_illum_events():
    # loop through each input - output couple
    for search_interval, expected_intervals in sat_illum_event_inputs_outputs():
        # find illuminated times
        illum_times = sat_illum_finder(
            search_interval, kep_propagator(), use_total_eclipse=True, planet=earth()
        )

        # print(illum_times)
        # print("--------")
        # make sure output and expected value are of the same length
        assert len(illum_times.intervals) == len(expected_intervals)

        # check each interval to ensure equality
        for interval, exp_interval in zip(illum_times.intervals, expected_intervals):
            # if not interval.is_equal(exp_interval):
            #     print(interval)
            #     print("--------")
            #     print(exp_interval)
            #     print("*********")

            assert interval.is_equal(exp_interval, tolerance=100 * u.ns)
