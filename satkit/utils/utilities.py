# satkit: Satellite Mission Analysis and Design for Python
#
# Copyright (C) 2023 Egemen Imre
#
# Licensed under GNU GPL v3.0. See LICENSE.rst for more info.
"""
Utility functions.

"""
from org.orekit.bodies import GeodeticPoint, OneAxisEllipsoid
from org.orekit.frames import TopocentricFrame, FramesFactory
from org.orekit.utils import IERSConventions, Constants


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
