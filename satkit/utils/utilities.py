# satkit: Satellite Mission Analysis and Design for Python
#
# Copyright (C) 2023 Egemen Imre
#
# Licensed under GNU GPL v3.0. See LICENSE.rst for more info.
"""
Utility functions.

"""
from collections import namedtuple

from org.orekit.bodies import GeodeticPoint, OneAxisEllipsoid
from org.orekit.frames import Frame, FramesFactory, TopocentricFrame
from org.orekit.models import AtmosphericRefractionModel
from org.orekit.propagation import Propagator
from org.orekit.time import AbsoluteDate
from org.orekit.utils import Constants, IERSConventions, TimeStampedPVCoordinates

from satkit import u
from satkit.time.timeinterval import TimeInterval

# Azimuth-Elevation-Range and Range Rate named tuple
AzElRng = namedtuple("AzElRng", ["t", "az", "el", "rng", "rng_rate"])


def init_topo_frame(
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


def compute_gnd_az_el(
    t: AbsoluteDate,
    gnd_pos: GeodeticPoint | TopocentricFrame,
    pvt: TimeStampedPVCoordinates,
    frame: Frame,
    planet: OneAxisEllipsoid = None,
    refraction_model: AtmosphericRefractionModel = None,
) -> AzElRng:
    """
    Computes the azimuth, elevation, range and range rate for a given position
    (e.g., of a satellite) and a ground location.

    This method is not limited to a ground location on Earth (as defined by the
    `planet` parameter).

    Atmospheric Refraction Model should be set to `None` for communications
    applications. It can be set to `EarthITU453AtmosphereRefraction` or
    `EarthStandardAtmosphereRefraction` (provided by Orekit) for visual
    or optical applications.

    Parameters
    ----------
    t
        Time for computation
    gnd_pos
        Ground position in geodetic coordinates (or the topocentric frame associated with it)
    pvt
        Coordinates of the object (e.g., satellite)
    frame
        Frame associated with the coordinates of the object
    planet
        The planet where the ground location is located. Defaults to WGS84 Earth.
    refraction_model
        Atmospheric Refraction Model, defaults to `None`

    Returns
    -------
    AzElRng
        Azimuth-Elevation-Range named tuple

    """
    # init topocentric frame
    topo_frame = init_topo_frame(gnd_pos, planet)

    # shorthand for position vector
    r = pvt.getPosition()

    # fill the coordinate values
    az = topo_frame.getAzimuth(r, frame, t)
    el = topo_frame.getElevation(r, frame, t)
    rng = topo_frame.getRange(r, frame, t)
    rng_rate = topo_frame.getRangeRate(pvt, frame, t)

    # add the refraction correction if needed
    if refraction_model:
        el = el + refraction_model.getRefraction(el)

    # return the final tuple (with units)
    return AzElRng(t, az * u.rad, el * u.rad, rng * u.m, rng_rate * u.m / u.s)


def compute_gnd_az_el_list(
    interval: TimeInterval,
    gnd_pos: GeodeticPoint | TopocentricFrame,
    propagator: Propagator,
    planet: OneAxisEllipsoid = None,
    refraction_model: AtmosphericRefractionModel = None,
    az_el_timestep=60 * u.sec,
) -> list[AzElRng]:
    """
    Computes the azimuth-elevation-range list within an interval, for an object flying
    over a ground location.

    This method is not limited to a ground location on Earth (as defined by the
    `planet` parameter).

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
    interval
        Computation interval for the az-el-rng values
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

    Returns
    -------
    list[AzElRng]
        List of azimuth-Elevation-Range named tuples

    """
    # init topocentric frame
    topo_frame = init_topo_frame(gnd_pos, planet)

    frame = propagator.getFrame()

    aer_list = []

    t = interval.start
    while t.isBefore(interval.end):
        pvt = propagator.getPVCoordinates(t, frame)

        aer_list.append(
            compute_gnd_az_el(t, topo_frame, pvt, frame, planet, refraction_model)
        )

        t += az_el_timestep

    # add the final step, just in case
    t = interval.end
    pvt = propagator.getPVCoordinates(t, frame)

    aer_list.append(
        compute_gnd_az_el(t, topo_frame, pvt, frame, planet, refraction_model)
    )

    return aer_list
