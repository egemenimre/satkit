# satkit: Satellite Mission Analysis and Design for Python
#
# Copyright (C) 2023 Egemen Imre
#
# Licensed under GNU GPL v3.0. See LICENSE.rst for more info.
"""
Package for `pint` Quantity object initialisers.

"""
from org.orekit.bodies import GeodeticPoint
from pint import Quantity

from satkit import u


class QuantityInit:
    """
    Helper class to initialise Orekit objects with `pint` Quantity support.
    """

    @staticmethod
    @u.wraps(None, ("rad", "rad", "m"), False)
    def geodetic_point(
        latitude: float | Quantity,
        longitude: float | Quantity,
        altitude: float | Quantity,
    ) -> GeodeticPoint:
        """
        Initialises an Orekit `GeodeticPoint` object with units support.

        Parameters
        ----------
        latitude
            Geodetic latitude [rad]
        longitude
            Geodetic longitude [rad]
        altitude
            Altitude over the ellipsoid [m]

        Returns
        -------
        geodetic_point
            Geodetic point on the ellipsoid

        """
        return GeodeticPoint(float(latitude), float(longitude), float(altitude))
