# satkit: Satellite Mission Analysis and Design for Python
#
# Copyright (C) 2023 Egemen Imre
#
# Licensed under GNU GPL v3.0. See LICENSE.rst for more info.
"""
Event finders for ground based events and intervals.
"""
from org.orekit.bodies import GeodeticPoint, OneAxisEllipsoid
from org.orekit.frames import TopocentricFrame
from org.orekit.propagation import Propagator
from org.orekit.propagation.events import ElevationDetector, EventsLogger
from org.orekit.propagation.events.handlers import ContinueOnEvent
from org.orekit.utils import ElevationMask
from pint import Quantity

from satkit import u
from satkit.time.timeinterval import TimeInterval, TimeIntervalList


@u.wraps(None, (None, None, None, "rad", None), False)
def gnd_pass_finder(
    search_interval: TimeInterval,
    propagator: Propagator,
    gnd_pos: GeodeticPoint,
    elev_mask: float | Quantity | ElevationMask,
    planet: OneAxisEllipsoid,
) -> TimeIntervalList:
    """
    Finds satellite (or any object with a trajectory) "passes" over a ground location.

    This method is not limited to a ground location on Earth (as defined by the `planet` parameter).
    It uses the Orekit `ElevationDetector` to find the "elevation equal to elevation mask" events.
    However, the cases with "no events in the search interval" are handled correctly. The output is
    a `TimeIntervalList` which can then be intersected with another interval list, for example
    "ground location illuminated intervals".

    The method accepts both a fixed elevation mask or an `ElevationMask` with a complex mask shape.

    The planet parameter can be any `OneAxisEllipsoid` with its own fixed frame. For example,
    Earth can be generated as follows:

        itrf = FramesFactory.getITRF(IERSConventions.IERS_2010, True)
        earth = OneAxisEllipsoid(Constants.WGS84_EARTH_EQUATORIAL_RADIUS,
                                 Constants.WGS84_EARTH_FLATTENING,
                                 itrf)

    Parameters
    ----------
    search_interval
        search interval for the "elevation events"
    propagator
        propagator to generate the trajectory of the satellite (or any other object)
    gnd_pos
        ground position in geodetic coordinates
    elev_mask
        Elevation mask, either a fixed value or a complex mask shape
    planet
        The planet where the ground location is located.

    Returns
    -------

    """

    # init topocentric frame
    topo_frame = TopocentricFrame(planet, gnd_pos, "ground pos")

    # event detector: Elevation Mask
    if isinstance(elev_mask, ElevationMask):
        # Use an elevation mask that is a function of azimuth angle
        elev_detector = ElevationDetector(topo_frame).withElevationMask(elev_mask)
    else:
        # Use a constant elevation mask
        elev_detector = ElevationDetector(topo_frame).withConstantElevation(elev_mask)

    elev_detector = elev_detector.withHandler(ContinueOnEvent())

    # add the event detector to the propagator
    logger = EventsLogger()
    propagator.addEventDetector(logger.monitorDetector(elev_detector))

    # Propagate from the initial date to the final date, logging increasing and decreasing events
    prop_end_state = propagator.propagate(search_interval.start, search_interval.end)

    # Categorise the events
    start_state = None
    intervals = []

    events = [event for event in logger.getLoggedEvents()]  # convert events to list

    if not events:
        # event list is empty, this means either the complete duration is valid or the complete duration is invalid
        if elev_detector.g(prop_end_state) > 0:
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
