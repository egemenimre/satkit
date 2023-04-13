# satkit: Satellite Mission Analysis and Design for Python
#
# Copyright (C) 2023 Egemen Imre
#
# Licensed under GNU GPL v3.0. See LICENSE.rst for more info.
"""
Event finders for ground based events and intervals.
"""
from enum import Enum

from org.orekit.bodies import CelestialBodyFactory, GeodeticPoint, OneAxisEllipsoid
from org.orekit.frames import FramesFactory, TopocentricFrame
from org.orekit.models import AtmosphericRefractionModel
from org.orekit.propagation import Propagator
from org.orekit.propagation.events import (
    EclipseDetector,
    ElevationDetector,
    EventsLogger,
    GroundAtNightDetector,
)
from org.orekit.propagation.events.handlers import ContinueOnEvent
from org.orekit.utils import (
    Constants,
    ElevationMask,
    IERSConventions,
    PVCoordinatesProvider,
)
from pint import Quantity

from satkit import u
from satkit.propagation.orbits import generate_ephemeris_prop
from satkit.time.timeinterval import TimeInterval, TimeIntervalList


@u.wraps(None, (None, None, "rad", None, None, None), False)
def gnd_pass_finder(
    search_interval: TimeInterval,
    gnd_pos: GeodeticPoint | TopocentricFrame,
    elev_mask: float | Quantity | ElevationMask,
    propagator: Propagator,
    planet: OneAxisEllipsoid = None,
    refraction_model: AtmosphericRefractionModel = None,
) -> TimeIntervalList:
    """
    Finds satellite (or any object with a trajectory) "passes" over a ground location.

    This method is not limited to a ground location on Earth (as defined by the
    `planet` parameter). It uses the Orekit `ElevationDetector` to find the
    "elevation equal to elevation mask" events. However, the cases with
    "no events in the search interval" are handled correctly. The output is
    a `TimeIntervalList` which can then be intersected with another interval list,
    for example "ground location illuminated intervals".

    The method accepts both a fixed elevation mask or an `ElevationMask`
    with a complex mask shape.

    The planet parameter can be any `OneAxisEllipsoid` with its own fixed frame.
    For example, Earth can be generated as follows::

        itrf = FramesFactory.getITRF(IERSConventions.IERS_2010, True)
        earth = OneAxisEllipsoid(Constants.WGS84_EARTH_EQUATORIAL_RADIUS,
                                 Constants.WGS84_EARTH_FLATTENING,
                                 itrf)

    If the `gnd_pos` parameter is defined as a `TopocentricFrame`, then the
    optional planet parameter is ignored. Otherwise, it is set to Earth as given above.

    Atmospheric Refraction Model should be set to `None` for communications
    applications. It can be set to `EarthITU453AtmosphereRefraction` or
    `EarthStandardAtmosphereRefraction` (provided by Orekit) for visual
    or optical applications.

    Parameters
    ----------
    search_interval
        Search interval for the "elevation events"
    propagator
        Propagator to generate the trajectory of the satellite (or any other object)
    gnd_pos
        Ground position in geodetic coordinates (or the topocentric frame associated with it)
    elev_mask
        Elevation mask, either a fixed value or a complex mask shape
    planet
        The planet where the ground location is located. Defaults to WGS84 Earth.
    refraction_model
        Atmospheric Refraction Model, defaults to `None`

    Returns
    -------
    TimeIntervalList
        List of time intervals corresponding to the "elevation above the mask"

    """

    # init topocentric frame
    topo_frame = _init_topo_frame(gnd_pos, planet)

    # Init event detector: Elevation Mask
    if isinstance(elev_mask, ElevationMask):
        # Use an elevation mask that is a function of azimuth angle
        event_detector = ElevationDetector(topo_frame).withElevationMask(elev_mask)
    else:
        # Use a constant elevation mask
        event_detector = ElevationDetector(topo_frame).withConstantElevation(elev_mask)

    # add atmospheric refraction model (or None)
    event_detector = event_detector.withRefraction(refraction_model)

    # do not stop at "rise" or "set" events (returns AbstractDetector)
    event_detector = event_detector.withHandler(ContinueOnEvent())

    # return the generated time interval list (g positive marks an interval)
    return _find_g_pos_intervals(search_interval, propagator, event_detector)


class StandardDawnDuskElevs(Enum):
    """Standard elevations definitions."""

    # Sun elevation at civil dawn/dusk (6° below horizon).
    CIVIL_DAWN_DUSK_ELEVATION = -6.0 * u.deg

    # Sun elevation at nautical dawn/dusk (12° below horizon).
    NAUTICAL_DAWN_DUSK_ELEVATION = -12.0 * u.deg

    # Sun elevation at astronomical dawn/dusk (18° below horizon).
    ASTRONOMICAL_DAWN_DUSK_ELEVATION = -18.0 * u.deg


@u.wraps(None, (None, None, "rad", None, None, None), False)
def gnd_illum_finder(
    search_interval: TimeInterval,
    gnd_pos: GeodeticPoint | TopocentricFrame,
    dawn_dusk_elev: float | Quantity | StandardDawnDuskElevs,
    sun_coords: PVCoordinatesProvider = None,
    planet: OneAxisEllipsoid = None,
    refraction_model: AtmosphericRefractionModel = None,
) -> TimeIntervalList:
    """
    Finds illumination periods of a ground location.

    This method is not limited to a ground location on Earth (as defined by the
    `planet` parameter). It uses the Orekit `GroundAtNightDetector` to find the
    "Sun elevation equal to elevation limit" events.
    However, the cases with "no events in the search interval" are handled correctly.
    The output is a `TimeIntervalList` which can then be intersected
    with another interval list, for example "satellite pass over ground location
    intervals".

    Sun positions are by default generated every 10 minutes and the underlying
    interpolator (the `Ephemeris` propagator) uses 5 data points.

    The method accepts both a fixed elevation mask or the values in the
    `StandardDawnDuskElevs` enumerator.

    The planet parameter can be any `OneAxisEllipsoid` with its own fixed frame.
    For example, Earth can be generated as follows::

        itrf = FramesFactory.getITRF(IERSConventions.IERS_2010, True)
        earth = OneAxisEllipsoid(Constants.WGS84_EARTH_EQUATORIAL_RADIUS,
                                 Constants.WGS84_EARTH_FLATTENING,
                                 itrf)

    If the `gnd_pos` parameter is defined as a `TopocentricFrame`, then the optional
    planet parameter is ignored. Otherwise, it is set to Earth as given above.

    Atmospheric Refraction Model should be set to `None` to ignore the atmospheric
    refraction. It can be set to `EarthITU453AtmosphereRefraction` or
    `EarthStandardAtmosphereRefraction` (provided by Orekit), though the ITU 453
    refraction model which can compute refraction at large negative
    elevations should be preferred. For visual applications, typically
    Astronomical Dawn/Dusk definition is used.


    Parameters
    ----------
    search_interval
        Search interval for the "events"
    gnd_pos
        Ground position in geodetic coordinates (or the topocentric frame associated with it)
    dawn_dusk_elev
        Elevation mask a fixed value
    sun_coords
        Propagator (or `PVCoordinatesProvider`) to generate the trajectory of the Sun
    planet
        The planet where the ground position is located. Defaults to WGS84 Earth.
    refraction_model
        Atmospheric Refraction Model, defaults to `None`

    Returns
    -------
    TimeIntervalList
        List of time intervals corresponding to the "sun elevation above the elev mask"
    """

    # Init topocentric frame
    topo_frame = _init_topo_frame(gnd_pos, planet)

    # generate Sun as a PVCoordinatesProvider
    if not sun_coords:
        sun_coords = PVCoordinatesProvider.cast_(CelestialBodyFactory.getSun())

    # Check elevation mask
    if isinstance(dawn_dusk_elev, StandardDawnDuskElevs):
        # Use the standard elevation mask but convert to radians
        dawn_dusk_elev = dawn_dusk_elev.value.m_as("rad")

    # Init event detector: Ground at Night
    event_detector = GroundAtNightDetector(
        topo_frame, sun_coords, float(dawn_dusk_elev), refraction_model
    )

    # Generate an Ephemeris Propagator to hold the trajectory of the Sun
    stepsize = 10 * 60 * u.sec
    interpolation_points = 5
    propagator = generate_ephemeris_prop(
        search_interval,
        sun_coords,
        stepsize=stepsize,
        frame=FramesFactory.getGCRF(),
        interpolation_points=interpolation_points,
    )

    # return the generated time interval list (g negative marks an interval)
    return _find_g_neg_intervals(search_interval, propagator, event_detector)


@u.wraps(None, (None, None, None, "rad", None, None), False)
def sat_illum_finder(
    search_interval: TimeInterval,
    propagator: Propagator,
    use_total_eclipse: bool = True,
    angular_margin: float | Quantity = 0.0,
    sun_coords: PVCoordinatesProvider = None,
    planet: OneAxisEllipsoid = None,
) -> TimeIntervalList:
    """
    Finds satellite (or any object with a trajectory) illumination (or outside
    occultation) times.

    This method computes the durations outside umbra or penumbra for a point object
    (e.g., a satellite) on a trajectory. It uses the Orekit `EclipseDetector` to find
    the umbra/penumbra entry and exit events. However, the cases with
    "no events in the search interval" are handled correctly.
    The output is a `TimeIntervalList` which can then be intersected
    with another interval list, for example "satellite pass over ground location
    intervals".

    The `use_total_eclipse` flag is used to find umbra or penumbra entry/exit events.
    The `angular_margin` parameter added to the eclipse detection. A positive margin
    implies eclipses are "larger" hence entry occurs earlier and exit occurs
    later than a detector with 0 margin.

    The planet parameter can be any `OneAxisEllipsoid` with its own fixed frame.
    For example, Earth can be generated as follows::

        itrf = FramesFactory.getITRF(IERSConventions.IERS_2010, True)
        earth = OneAxisEllipsoid(Constants.WGS84_EARTH_EQUATORIAL_RADIUS,
                                 Constants.WGS84_EARTH_FLATTENING,
                                 itrf)

    The same method can be used to find eclipses due to the Moon, by simply replacing the
    `planet` parameter with the Moon definition.

    Parameters
    ----------
    search_interval
        Search interval for the "events"
    propagator
        Propagator to generate the trajectory of the satellite (or any other object)
    use_total_eclipse
        Total eclipse detection flag (true for umbra events detection, false for penumbra events detection)
    angular_margin
        Angular margin added to the eclipse detection
    sun_coords
        Propagator (or `PVCoordinatesProvider`) to generate the trajectory of the Sun
    planet
        The planet where the ground position is located. Defaults to WGS84 Earth.


    Returns
    -------
    TimeIntervalList
        List of time intervals corresponding to the "elevation above the mask"
    """

    # generate Sun as a PVCoordinatesProvider
    if not sun_coords:
        sun_coords = PVCoordinatesProvider.cast_(CelestialBodyFactory.getSun())

    # Init event detector: Eclipse
    sun_radius = Constants.SUN_RADIUS  # meters
    event_detector = EclipseDetector(sun_coords, sun_radius, planet)

    # TODO delete the try except block when Orekit 12 is available
    try:
        event_detector = event_detector.withMargin(angular_margin)
    except AttributeError:
        pass

    # check for umbra / penumbra
    if use_total_eclipse:
        event_detector = event_detector.withUmbra()
    else:
        event_detector = event_detector.withPenumbra()

    # do not stop at "start" or "end" events (returns AbstractDetector)
    event_detector = event_detector.withHandler(ContinueOnEvent())

    # return the generated time interval list (g positive marks an interval)
    return _find_g_pos_intervals(search_interval, propagator, event_detector)


def _find_g_pos_intervals(
    search_interval: TimeInterval, propagator: Propagator, event_detector
) -> TimeIntervalList:
    """
    Finds the intervals where the `g` function is positive. Increasing `g` event
    marks the start of the interval and decreasing `g` event marks the end of
    the interval.

    Parameters
    ----------
    search_interval
        Search interval for the "events"
    propagator
        Propagator to generate the trajectory of the satellite (or any other object)
    event_detector
        Event detector

    Returns
    -------
    TimeIntervalList
        Time interval list conforming to the events

    """
    # add the event detector to the propagator
    logger = EventsLogger()
    propagator.addEventDetector(logger.monitorDetector(event_detector))

    # Propagate from the initial date to the final date, logging increasing and decreasing events
    prop_end_state = propagator.propagate(search_interval.start, search_interval.end)

    # Categorise the events

    # for g()>0, event is in interval
    start_state = None
    intervals = []

    events = [event for event in logger.getLoggedEvents()]  # convert events to list

    if not events:
        # event list is empty, this means either the complete duration is valid or the complete duration is invalid
        if event_detector.g(prop_end_state) > 0:
            # the complete duration is an event
            intervals = [TimeInterval.from_interval(search_interval)]
        return TimeIntervalList(intervals, search_interval)
    else:
        # event list is not empty, process events

        if events[-1].isIncreasing():
            # last event is the beginning of a pass, set the end of the pass to search end
            intervals.append(
                TimeInterval(events[-1].getState().getDate(), search_interval.end)
            )
            # remove the item
            events.remove(events[-1])

        if not events[0].isIncreasing():
            # first event is end of a pass, set the beginning of the pass to search begin
            intervals.append(
                TimeInterval(search_interval.start, events[0].getState().getDate())
            )
            # remove the item
            events.remove(events[0])

        for event in events:
            # process the remaining events normally - they have proper begin and end dates with events

            if event.isIncreasing():
                start_state = event.getState()
            elif start_state:
                stop_state = event.getState()
                intervals.append(
                    TimeInterval(start_state.getDate(), stop_state.getDate())
                )
                start_state = None

    # return the generated time interval list
    return TimeIntervalList(intervals, search_interval)


def _find_g_neg_intervals(
    search_interval: TimeInterval, propagator: Propagator, event_detector
) -> TimeIntervalList:
    """
    Finds the intervals where the g function is negative. Increasing `g` event
    marks the end of the interval and decreasing `g` event marks the start of
    the interval.

    Parameters
    ----------
    search_interval
        Search interval for the "events"
    propagator
        Propagator to generate the trajectory of the satellite (or any other object)
    event_detector
        Event detector

    Returns
    -------
    TimeIntervalList
        Time interval list conforming to the events

    """
    return _find_g_pos_intervals(search_interval, propagator, event_detector).invert()


def _init_topo_frame(
    gnd_pos: GeodeticPoint | TopocentricFrame,
    planet: OneAxisEllipsoid = None,
) -> TopocentricFrame:
    """
    Initialises the Topocentric Frame.

    Parameters
    ----------
    gnd_pos
        Ground position in geodetic coordinates (or the topocentric frame associated with it)
    planet
        The planet where the ground position is located. Defaults to WGS84 Earth.

    Returns
    -------
    TopocentricFrame
        Topocentric frame belonging to the Ground Position

    """
    # init topocentric frame
    if isinstance(gnd_pos, GeodeticPoint):
        # ground position given as GeodeticPoint
        if planet:
            # planet is defined, use it
            topo_frame = TopocentricFrame(planet, gnd_pos, "ground pos")
        else:
            # planet is not defined, use the default WGS84 Earth
            itrf = FramesFactory.getITRF(IERSConventions.IERS_2010, True)
            earth = OneAxisEllipsoid(
                Constants.WGS84_EARTH_EQUATORIAL_RADIUS,
                Constants.WGS84_EARTH_FLATTENING,
                itrf,
            )
            topo_frame = TopocentricFrame(earth, gnd_pos, "ground pos")

    else:
        # ground position given directly as TopocentricFrame, just copy it
        topo_frame = gnd_pos

    return topo_frame
