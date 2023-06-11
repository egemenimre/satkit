# satkit: Satellite Mission Analysis and Design for Python
#
# Copyright (C) 2023 Egemen Imre
#
# Licensed under GNU GPL v3.0. See LICENSE.rst for more info.
"""
Module for ground-based accesses and passes.

"""

from org.orekit.bodies import GeodeticPoint, OneAxisEllipsoid
from org.orekit.frames import TopocentricFrame
from org.orekit.models import AtmosphericRefractionModel
from org.orekit.propagation import Propagator
from org.orekit.time import AbsoluteDate
from org.orekit.utils import ElevationMask
from pint import Quantity

from satkit import u
from satkit.events.eventfinders import gnd_pass_finder
from satkit.time.timeinterval import TimeInterval
from satkit.utils.utilities import (
    compute_gnd_az_el,
    compute_gnd_az_el_list,
    init_topo_frame,
)


@u.wraps(None, (None, None, None, None, None, None, "sec"), False)
class GroundPass:
    """
    Parameters associated with a "pass" (line-of-sight availability) over
    a ground location.

    A "pass" could be a satellite communications pass over a ground station
    or an observation opportunity for a ground observation station. The object
    then holds information such as pass duration, peak elevation time and value
    and azimuth-elevation-range list.

    The constructor computes the pass properties given the pass time interval.
    For RF applications (e.g., radar or comms) atmospheric refraction should *not*
    be used. Atmospheric refraction is useful for optical applications (e.g.,
    satellite tracking with a telescope).

    Usually this object is not created manually, but is an outcome of the calculation
    of a list of passes over a ground location.

    Parameters
    ----------
    pass_interval
        Time interval of the pass (shallow copied into the object)
    max_elev_time
        Time of maximum elevation (shallow copied into the object)
    gnd_pos
        Ground position in geodetic coordinates (or the topocentric frame associated with it)
    propagator
        Propagator to generate the trajectory of the satellite (or any other object)
    planet
        The planet where the ground location is located. Defaults to WGS84 Earth.
    refraction_model
        Atmospheric Refraction Model, defaults to `None`
    az_el_timestep
        Stepsize for the azimuth-elevation-range list
    """

    def __init__(
        self,
        pass_interval: TimeInterval,
        max_elev_time: AbsoluteDate,
        gnd_pos: GeodeticPoint | TopocentricFrame,
        propagator: Propagator,
        planet: OneAxisEllipsoid = None,
        refraction_model: AtmosphericRefractionModel = None,
        az_el_timestep=60 * u.sec,
    ):
        # shallow copy the interval
        self.pass_interval = pass_interval

        # shallow copy the max elevation time
        self.max_elev_time = max_elev_time

        # compute max elevation AER values
        frame = propagator.getFrame()
        pvt_max_elev = propagator.getPVCoordinates(max_elev_time, frame)

        self.max_elev_aer = compute_gnd_az_el(
            max_elev_time, gnd_pos, pvt_max_elev, frame, planet, refraction_model
        )

        # compute az-el list (with atmospheric refraction where necessary)
        self.az_el_list = compute_gnd_az_el_list(
            pass_interval,
            gnd_pos,
            propagator,
            planet,
            refraction_model,
            az_el_timestep,
        )


class GroundPassList:
    @u.wraps(None, (None, None, None, "rad", None, None, None, "sec"), False)
    def __init__(
        self,
        search_interval: TimeInterval,
        gnd_pos: GeodeticPoint | TopocentricFrame,
        elev_mask: float | Quantity | ElevationMask,
        propagator: Propagator,
        planet: OneAxisEllipsoid = None,
        refraction_model: AtmosphericRefractionModel = None,
        az_el_timestep=60 * u.sec,
    ):
        """
        Parameters associated with a list of "passes" (line-of-sight availability)
        over a ground location.

        The constructor computes the pass properties given the search interval.
        A "pass" could be a satellite communications pass over a ground station or
        an observation opportunity for a ground observation station. The object then
        holds information such as pass duration, peak elevation time and value as well as
        azimuth-elevation-range list for multiple such passes or `GroundPass` objects.

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
        gnd_pos
            Ground position in geodetic coordinates (or the topocentric frame associated with it)
        elev_mask
            Elevation mask, either a fixed value or a complex mask shape
        propagator
            Propagator to generate the trajectory of the satellite (or any other object)
        planet
            The planet where the ground location is located. Defaults to WGS84 Earth.
        refraction_model
            Atmospheric Refraction Model, defaults to `None`
        az_el_timestep
            Stepsize for the azimuth-elevation-range list
        """

        # init topocentric frame
        topo_frame = init_topo_frame(gnd_pos, planet)

        # find the ground pass intervals and max elevations
        self.pass_intervals, max_elev_times = gnd_pass_finder(
            search_interval,
            topo_frame,
            elev_mask,
            propagator,
            planet,
            refraction_model,
        )

        # compute the Ground Passes
        self.pass_list = []

        for interval, max_elev_time in list(
            zip(self.pass_intervals.intervals, max_elev_times)
        ):
            # compute the pass details
            gnd_pass = GroundPass(
                interval,
                max_elev_time,
                topo_frame,
                propagator,
                planet,
                refraction_model,
                az_el_timestep,
            )

            self.pass_list.append(gnd_pass)
