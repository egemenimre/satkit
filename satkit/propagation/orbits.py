# satkit: Satellite Mission Analysis and Design for Python
#
# Copyright (C) 2023 Egemen Imre
#
# Licensed under GNU GPL v3.0. See LICENSE.rst for more info.
"""
Orbit helper methods.
"""
import numpy as np
from org.orekit.utils import Constants
from pint import Quantity

from satkit import u


class OrbitUtils:
    """
    Utilities for orbits.

    Basic conversions and functions of orbit related operations for convenience.
    """

    @staticmethod
    @u.wraps("m", "rad/s", False)
    def compute_sma(mean_mot: float | Quantity) -> Quantity:
        """
        Computes the (mean) semimajor axis from the mean motion.

        Equations use WGS84 parameters for mu.

        Parameters
        ----------
        mean_mot :  float or Quantity
            Mean Motion [rad/s]

        Returns
        -------
        sma
            Semimajor axis with units [m]
        """

        # Quantity input guaranteed to be in [rad/s], converted to float.
        # Float input processed as-is, assumed to be in correct units.

        return np.power(Constants.WGS84_EARTH_MU / mean_mot**2, 1.0 / 3.0) * u.m

    @staticmethod
    @u.wraps("rad/s", "m", False)
    def compute_mean_mot(a: float | Quantity) -> Quantity:
        """
        Computes the (mean) mean motion axis from the semimajor axis.

        Equations use WGS84 parameters for mu.

        Parameters
        ----------
        a :  float or Quantity
            Semimajor axis [m]

        Returns
        -------
        sma
            Mean motion with units [rad/s]
        """

        # Quantity input guaranteed to be in [m], converted to float.
        # Float input processed as-is, assumed to be in correct units.

        return np.sqrt(Constants.WGS84_EARTH_MU / a**3) * u.rad / u.s

    @staticmethod
    @u.wraps("rad/s", ("m", None, "rad", None), False)
    def compute_raan_drift_rate(
        sma: float | Quantity,
        eccentricity: float,
        inclination: float | Quantity,
        include_j4: bool = True,
    ) -> Quantity:
        """
        Computes the RAAN (or orbital plane) drift rate.

        The orbit plane rotation rate is calculated via a J4 secular drift rate (See
        Fundamentals of Astrodynamics Vallado 4th ed pg. 650).

        Equations use WGS84 parameters for Earth equator radius and mu.
        J2 and J4 are from EGM96.

        Parameters
        ----------
        sma
            (mean) semimajor axis [m]
        eccentricity
            (mean) eccentricity of the orbit [dimensionless]
        inclination
            (mean) inclination [rad]
        include_j4
            True if J2^2 and J4 effects are to be included, False for J2 only.

        Returns
        -------
        raan_drift_rate
            RAAN drift rate in angles/time (e.g. deg/day)
        """

        # R_E in m
        r_e = Constants.WGS84_EARTH_EQUATORIAL_RADIUS * u.m
        # MU in m3/s2
        mu = Constants.WGS84_EARTH_MU * u["m**3/s**2"]

        e = eccentricity

        # Inclination in radians
        i = inclination if isinstance(inclination, u.Quantity) else inclination * u.rad
        #  semimajor axis in metres
        a = sma if isinstance(sma, u.Quantity) else sma * u.m
        p = a * (1.0 - e**2)
        n = np.sqrt(mu / a**3)

        # Set J2 and J4 (EGM96)
        j2 = 0.0010826266835531513
        j4 = -1.619621591367e-06
        # j6 = 5.406812391070849e-07

        # drift rate in angles/time (e.g. deg/day)
        # check for the J4 flag
        if include_j4:
            return (
                -(3.0 * j2 * r_e**2 * n * np.cos(i)) / (2.0 * p**2)
                + (3.0 * j2**2 * r_e**4 * n * np.cos(i))
                / (32.0 * p**4)
                * (12.0 - 4 * e**2 - (80 + 5 * e**2) * (np.sin(i)) ** 2)
                + (15.0 * j4 * r_e**4 * n * np.cos(i))
                / (32.0 * p**4)
                * (8.0 + 12 * e**2 - (14 + 21 * e**2) * (np.sin(i)) ** 2)
                # - (105.0 * j6 * r_e**6 * n * np.cos(i))
                # / (1024.0 * p**6)
                # * (
                #     64.0
                #     + 160.0 * e**2
                #     + 120.0 * e**4
                #     - (288.0 + 720 * e**2 + 540 * e**4) * (np.sin(i)) ** 2
                #     + (264.0 + 660 * e**2 + 495 * e**4) * (np.sin(i)) ** 4
                # )
            )
        else:
            return -(3.0 * j2 * r_e**2 * n * np.cos(i)) / (2.0 * p**2)
