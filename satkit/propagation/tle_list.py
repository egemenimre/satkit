# satkit: Satellite Mission Analysis and Design for Python
#
# Copyright (C) 2023 Egemen Imre
#
# Licensed under GNU GPL v3.0. See LICENSE.rst for more info.
"""
TLE list helper functions.
"""
from abc import ABC
from copy import copy
from enum import Enum
from typing import List

from orekit.pyhelpers import absolutedate_to_datetime
from org.orekit.propagation.analytical.tle import TLE
from org.orekit.time import AbsoluteDate

from satkit.propagation.tle import TleDefaultUnits


class TleRangeFilterParams(Enum):
    """TLE Filtering Parameters."""

    EPOCH = "date"
    DATE = "date"
    SAT_NR = "satelliteNumber"
    LAUNCH_NR = "launchNumber"
    LAUNCH_YR = "launchYear"
    INCL = "i"
    INCLINATION = "i"
    E = "e"
    ECCENTRICITY = "e"
    MEAN_ANOMALY = "meanAnomaly"
    ARG_OF_PERIGEE = "perigeeArgument"
    RAAN = "raan"
    MEAN_MOTION = "meanMotion"
    N = "meanMotion"
    N_DOT = "meanMotionFirstDerivative"
    N_DOT_DOT = "meanMotionSecondDerivative"
    BSTAR = "bStar"
    ELEMENT_NR = "elementNumber"
    REV_NR = "revolutionNumberAtEpoch"


class TleValueFilterParams(Enum):
    """TLE Filtering Parameters."""

    SAT_NR = "satelliteNumber"
    LAUNCH_NR = "launchNumber"
    LAUNCH_PIECE = "launchPiece"
    LAUNCH_YR = "launchYear"
    CLASSIFICATION = "classification"
    EPHEMERIS_TYPE = "ephemerisType"
    ELEMENT_NR = "elementNumber"
    REV_NR = "revolutionNumberAtEpoch"


class _TleList(ABC):
    """Abstract Base Class for TLE lists."""

    tle_list: List[TLE] = []

    def filter_by_value(self, param: TleValueFilterParams, value):
        """
        Filters the TLE list for equivalence to a given value.

        For example `param` can be equal to `TleFilterParams.SAT_NR` and `value`
        can be equal to `46945`, which filters all TLEs with a sat number 46945.

        Note that this filter is not appropriate for float values such as eccentricity
        where equivalence is very brittle. For these applications, use
        `filter_by_range()` or `filter_by_func()` instead.

        This method returns a `TleStorage` object even if the filtering result is empty.
        In this case, `tle_list` parameter of the `TleStorage` object will be an empty
        list.

        Also note that, the returned TLE objects in the list are just shallow copies
        of the objects in the master TLE list. Any change to them will change the
        relevant item in the backing TLE list.

        Parameters
        ----------
        param
            Filter parameter (such as name or satellite number)
        value
            Value associated with the parameter

        Returns
        -------
        TleStorage
            A `TleStorage` object that contains the filtered list of TLE data

        Raises
        ------
        ValueError
            TleFilterParams.TLE is given as an input
        """

        filtered_list = [
            tle for tle in self.tle_list if getattr(tle, str(param.value)) == value
        ]

        # create new object with the filtered list
        return self._selfcopy(filtered_list)

    def filter_by_func(self, filter_func):
        """
        Filters the TLE list for compliance to a given filter function.

        The `filter_func` should be a filtering function that tests the TLE
        and returns `True` or `False` accordingly. This method is useful for
        more complicated filters for the entire TLE (for example filters with
        `and` or `or` can be constructed, filtering for two parameters
        simultaneously).

        The following function filters for semi-major axis values above 7000 km.
        Note that units should be defined and compatible with the value to be
        compared against. For semimajor axis, distance units such as meters
        are acceptable but using no dimensions or using wrong units
        (such as degrees) will throw an error.

        >>> from satkit import u
        >>> from satkit.propagation.tle import TLEUtils
        >>>
        >>> def sma_filter(tle):
        >>>     return True if TLEUtils.compute_sma(tle) > 7000 * u.km else False

        For exact equivalences (such as satellite names or ID numbers),
        using `filter_by_value` method will be easier and more appropriate.
        For simple range checks, `filter_by_range` should be used.

        This method returns a `TleStorage` object even if the filtering result is empty.
        In this case, `tle_list` parameter of the `TleStorage` object will be an empty
        list.

        Also note that, the returned TLE objects in the list are just shallow copies
        of the objects in the master TLE list. Any change to them will change the
        relevant item in the backing TLE list.

        Parameters
        ----------
        filter_func
            Function to test the parameter against

        Returns
        -------
        TleStorage
            A `TleStorage` object that contains the filtered list of TLE data
        """
        filtered_list = [tle for tle in self.tle_list if filter_func(tle)]

        # create new object with the filtered list
        return self._selfcopy(filtered_list)

    def filter_by_range(
            self,
            param: TleRangeFilterParams,
            min_value=None,
            max_value=None,
            includes_bounds=False,
    ):
        """
        Filters the TLE list for compliance to a given min/max values.

        The test is simply:

        `max_value > param > min_value`

        or, if `includes_bounds` set to `True`:

        `max_value >= param >= min_value`

        For example `param` can be equal to `TleFilterParams.INCLINATION`, then
        this parameter is tested against the minimum and maximum inclination values
        supplied. If `None` is supplied for `min_value` or `max_value`, then there
        is no range or range check defined for this parameter. For example,
        if `min_value` is `None`, the parameter check reduces to `max_value > param`.

        Note that units should be defined and compatible with the value to be
        compared against. For inclination, angle units such as degrees are
        acceptable but using no dimensions or using wrong units (such as degrees)
        will throw an error.

        For time comparisons, min and max values can be `datetime` or `AbsoluteDate`
        objects.

        Semimajor axis comparisons should be carried out via Mean Motion parameter
        or using the `filter_by_func()` method.

        For exact equivalences (such as satellite names or ID numbers),
        using `filter_by_value` method will be easier and more appropriate.

        This method returns a `TleStorage` object even if the filtering result is empty.
        In this case, `tle_list` parameter of the `TleStorage` object will be an empty
        list.

        Also note that, the returned TLE objects in the list are just shallow copies
        of the objects in the master TLE list. Any change to them will change the
        relevant item in the backing TLE list.

        Parameters
        ----------
        param : TleRangeFilterParams
            Filter parameter (such as inclination or satellite number)
        min_value
            Minimum value to test the parameter against
        max_value
            Maximum value to test the parameter against
        includes_bounds
            `True` if bounds are to be included, `False` otherwise

        Returns
        -------
        TleStorage
            A `TleStorage` object that contains the filtered list of TLE data

        Raises
        ------
        ValueError
            TleFilterParams.TLE is given as an input
        """

        # date/time filtering is a special case
        if param.value == "date":
            # convert min and max values to datetime if needed
            min_value = (
                absolutedate_to_datetime(min_value)
                if isinstance(min_value, AbsoluteDate)
                else min_value
            )
            max_value = (
                absolutedate_to_datetime(max_value)
                if isinstance(max_value, AbsoluteDate)
                else max_value
            )

            # comparison function is time (filter_param not used, for compatibility only)
            def comp_func(tle: TLE, filter_param: TleRangeFilterParams):
                return absolutedate_to_datetime(tle.getDate())

        # all other filtering cases
        else:
            # `min_value` and `max_value` may be quantities and should be checked explicitly
            # strip units and convert before filtering
            if TleDefaultUnits[param.name].value:
                unit = TleDefaultUnits[param.name].value
                if max_value:
                    max_value = max_value.m_as(unit)
                if min_value:
                    min_value = min_value.m_as(unit)

            # comparison function is the selected parameter value
            def comp_func(tle: TLE, filter_param: TleRangeFilterParams):
                return getattr(tle, str(filter_param.value), None)

        # now generate the lists with the comparator functions

        # for `None`, otherwise can be interpreted as `True` or `False`.
        if min_value is not None and max_value is not None:

            def check_func(tle: TLE, filter_param: TleRangeFilterParams):
                return (
                    max_value >= comp_func(tle, param) >= min_value
                    if includes_bounds
                    else max_value > comp_func(tle, param) > min_value
                )

            filtered_list = [tle for tle in self.tle_list if check_func(tle, param)]
        elif min_value is not None:

            def check_func(tle: TLE, filter_param: TleRangeFilterParams):
                return (
                    comp_func(tle, param) >= min_value
                    if includes_bounds
                    else comp_func(tle, param) > min_value
                )

            filtered_list = [tle for tle in self.tle_list if check_func(tle, param)]
        elif max_value is not None:

            def check_func(tle: TLE, filter_param: TleRangeFilterParams):
                return (
                    max_value >= comp_func(tle, param)
                    if includes_bounds
                    else max_value > comp_func(tle, param)
                )

            filtered_list = [tle for tle in self.tle_list if check_func(tle, param)]
        else:
            filtered_list = []

        # create new object with the filtered list
        return self._selfcopy(filtered_list)

    def _selfcopy(self, new_list):
        """Creates a new (shallow copied) object of the same type with the new list."""
        output = copy(self)
        output.tle_list = new_list

        return output


class TleTimeSeries(_TleList):
    """TLE storage class that keeps a list of TLE data from a single satellite,
    at multiple times and with time order.

    The entry point is ideally the `TleStorage` class, where a TLE file is usually read,
    and a single satellite is filtered. Once this class is initialised, various sublists
    (e.g. specific time range) can be derived.

    Parameters
    ----------
    tle_list : list[TLE]
        initial list of TLE objects (shallow copied into object)
    """

    def __init__(self, tle_list, sat_number):
        # init a TLE Storage and filter for the sat number
        self.tle_list = (
            TleStorage(tle_list)
            .filter_by_value(TleValueFilterParams.SAT_NR, sat_number)
            .tle_list
        )

        # order the internal TLE list with respect to epoch
        # TLE date object does not have comparators, use Python datetime object
        self.tle_list.sort(key=lambda tle: absolutedate_to_datetime(tle.getDate()))


class TleStorage(_TleList):
    """TLE storage class that keeps a list of TLE data from multiple satellites,
    at multiple times and without any ordering.

    This class is the entry point for reading a TLE file, from which various sublists
    (e.g. single satellite, all LEO sats etc.) can be derived.

    Parameters
    ----------
    tle_list : list[TLE]
        initial list of TLE objects (shallow copied into object)
    """

    def __init__(self, tle_list):
        self.tle_list = tle_list

    @classmethod
    def from_path(cls, tle_file_path):
        """
        Read a set of TLE data from file. Tries to extract satellite names from the
        list, if no name is found, an empty string (not `None`) is assigned.

        Parameters
        ----------
        tle_file_path : Path
            Path of the text file to be read

        Returns
        -------
        TleStorage
            A `TleStorage` object that contains the list of TLE data
        """
        with open(tle_file_path, "r") as f:
            tle_source_str = f.read()

        return cls.from_string(tle_source_str)

    @classmethod
    def from_string(cls, tle_string):
        """
        Read a set of TLE data from a text. Tries to extract satellite names from the
        list, if no name is found, an empty string (not `None`) is assigned.

        Parameters
        ----------
        tle_string : str
            String containing successive TLE data

        Returns
        -------
        TleStorage
            A `TleStorage` object that contains the list of TLE data
        """

        tle_source_str = tle_string.split("\n")

        # create object without calling `__init__`
        tle_storage = cls.__new__(cls)

        # parse the string and load parsed items into list
        tle_storage.tle_list = _parse_tle_list(tle_source_str)

        return tle_storage

    def to_tle_timeseries(self, sat_number):
        """
        Filters the TLE list for a single satellite to initialise a `TleTimeSeries`.

        Parameters
        ----------
        sat_number
            Satellite Catalog Number

        Returns
        -------
        TleTimeSeries
            A `TleTimeSeries` object that contains the list of TLE data of a single
            satellite

        """
        return TleTimeSeries(self.tle_list, sat_number)


def _parse_tle_list(tle_source_str_list):
    """
    Parses the TLE list.

    Parameters
    ----------
    tle_source_str_list : list[str]
        TLE data as a list of strings.

    Returns
    -------
    tle_list : list[TLE]
        List of TLE data
    """

    tle_list = []

    name = line1 = line2 = None
    for i, line in enumerate(tle_source_str_list):

        # strip spaces and EOF around the line
        line = line.strip()
        # skip empty lines
        if not line.strip():
            continue

        if __is_tle_line(line, 1):
            line1 = line
            if __is_tle_line(tle_source_str_list[i + 1], 2):
                line2 = tle_source_str_list[i + 1]
                if i > 0 and (
                        not __is_tle_line(tle_source_str_list[i - 1], 1)
                        and not __is_tle_line(tle_source_str_list[i - 1], 2)
                ):
                    name = tle_source_str_list[i - 1].strip("\n ")
                    if name.startswith("0 "):
                        name = name[2:]

        if line1 and line2:
            tle = TLE(line1, line2)
            tle_list.append(tle)
            # reset temp fields
            name = line1 = line2 = None

    return tle_list


def __is_tle_line(line, line_nr):
    """Checks whether line is of type Line 1 or Line 2 standard TLE line."""
    if line.strip().startswith(f"{line_nr} "):
        return True
    else:
        return False
