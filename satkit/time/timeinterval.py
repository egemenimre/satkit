# satkit: Satellite Mission Analysis and Design for Python
#
# Copyright (C) 2023 Egemen Imre
#
# Licensed under GNU GPL v3.0. See LICENSE.rst for more info.
"""
Time interval module.

`TimeInterval` class stores time intervals and `TimeIntervalList` class stores
lists of `TimeInterval` objects.
"""

import portion as p
from org.orekit.time import AbsoluteDate, TimeStamped
from pint import Quantity
from portion import Interval

from satkit import u
from satkit.time.time import AbsoluteDateExt

_EPS_TIME = 10 * u.ns
"""Allowable time threshold, this much 'out of bounds' is allowed when assuming two
instances of time are *practically* equal. This helps with floating point artifacts
such as round-off errors."""


class TimeInterval:
    """
    Represent and manipulate a single time interval.

    This is a thin wrapper around the  :class:`Interval` class
    from `portion` package (for the Atomic intervals), using
    `AbsoluteDateExt` classes under the hood.
    """

    _interval: Interval = None

    def __init__(
        self,
        start_time: type[AbsoluteDate],
        end_time: type[AbsoluteDate],
        start_inclusive=True,
        end_inclusive=True,
    ):
        # upgrade to AbsoluteDateExt and deep copy in the process
        start_interval = AbsoluteDateExt(start_time)
        end_interval = AbsoluteDateExt(end_time)

        # Initialise the interval
        _interval = p.closed(start_interval, end_interval).replace(
            left=start_inclusive, right=end_inclusive
        )

        self._interval = _interval

    @classmethod
    def _validate(cls, start_time, end_time) -> bool:
        if isinstance(start_time, AbsoluteDate) and isinstance(end_time, AbsoluteDate):
            # start and end times are AbsoluteDate or a subclass

            if start_time.isAfter(end_time):
                # end time is earlier than start time - raise error
                raise ValueError(
                    f"End time ({end_time}) is earlier than start time"
                    f"({start_time})"
                )

        else:
            # One or both of start and end dates are of wrong type
            if not isinstance(end_time, type[AbsoluteDate]):
                raise ValueError(
                    f"End time is an instance of {end_time.__class__()}, "
                    f"only type[AbsoluteDate] (e.g., AbsoluteDateExt) classes are allowed."
                )
            if not isinstance(start_time, type[AbsoluteDate]):
                raise ValueError(
                    f"Start time is an instance of {start_time.__class__()}, "
                    f"only type[AbsoluteDate] (e.g., AbsoluteDateExt) classes are allowed."
                )

        # check for empty instances
        if start_time.isCloseTo(end_time, _EPS_TIME.m_as("sec")):
            return False

        return True

    def __new__(
        cls,
        start_time: type[AbsoluteDate],
        end_time: type[AbsoluteDate],
        start_inclusive=True,
        end_inclusive=True,
    ):
        # validate the inputs
        if cls._validate(start_time, end_time):
            return super().__new__(cls)

    @u.wraps(None, (None, "s", None, None), False)
    @staticmethod
    def from_duration(
        start_time: type[AbsoluteDate],
        duration: float | Quantity,
        start_inclusive=True,
        end_inclusive=True,
    ) -> "TimeInterval":
        """
        Generates a TimeInterval object from a start time and a duration.

        Parameters
        ----------
        start_time : Type[AbsoluteDate]
            Start time
        duration : Quantity of float
            duration [seconds]
        start_inclusive : bool
            True if the start of the interval is inclusive (closed), False if exclusive
            (open)
        end_inclusive : bool
            True if the start of the interval is inclusive (closed), False if exclusive
            (open)

        Returns
        -------
        TimeInterval
            The new TimeInterval object

        """
        return TimeInterval(
            start_time,
            start_time.shiftedBy(float(duration)),
            start_inclusive=start_inclusive,
            end_inclusive=end_inclusive,
        )

    @staticmethod
    def from_interval(interval: "TimeInterval") -> "TimeInterval":
        """
        Generates a deep copy of the TimeInterval object.

        Parameters
        ----------
        interval : TimeInterval
            TimeInterval to be copied

        Returns
        -------
        TimeInterval
            The new, deep copied TimeInterval object

        """
        return TimeInterval(
            interval.start,
            interval.end,
            start_inclusive=interval.is_start_inclusive,
            end_inclusive=interval.is_end_inclusive,
        )

    def is_in_interval(self, time):
        """
        Checks whether the requested time is within the time interval.

        Parameters
        ----------
        time : Time
            Time to be checked

        Returns
        -------
        bool
            True if time is within the reference interval, False otherwise
        """
        # check upper and lower boundaries for tolerance
        is_start_equal = time.isCloseTo(self.start, _EPS_TIME)
        is_end_equal = time.isCloseTo(self.end, _EPS_TIME)

        # check start
        if is_start_equal:
            # time at starting edge - is edge closed?
            if self._interval.left:
                return True
            else:
                return False

        # check end
        if is_end_equal:
            # time at end edge - is edge closed?
            if self._interval.right:
                return True
            else:
                return False

        # Time not edges, do a regular check
        return self._interval.contains(time)

    def is_equal(self, interval, tolerance=_EPS_TIME):
        """
        Checks whether two intervals are (almost) equal in value.

        If the two start or end values are as close as `tolerance`, then they are
        assumed to be equal in value. The default tolerance is given in `_EPS_TIME`
        and is on the order of nanoseconds.

        Parameters
        ----------
         interval : TimeInterval
            Time interval to be checked

        tolerance : float or Quantity
            the separation, in seconds, under which the two bounds of the interval will be
            considered close to each other

        Returns
        -------
        bool
            True if interval start and end are (almost) equal, False otherwise

        """
        is_start_equal = interval.start.isCloseTo(self.start, tolerance)
        is_end_equal = interval.end.isCloseTo(self.end, tolerance)

        return True if is_start_equal and is_end_equal else False

    def contains(self, interval):
        """
        Checks whether the requested interval is contained within this (self) interval.

        Parameters
        ----------
        interval : TimeInterval
            Time interval to be checked

        Returns
        -------
        bool
            True if check interval is contained within this interval,
            False otherwise
        """
        if self.is_in_interval(interval.start) and self.is_in_interval(interval.end):
            return True
        else:
            return False

    def is_intersecting(self, interval):
        """
        Checks whether the requested interval intersects (or is contained within)
        the reference interval.

        Parameters
        ----------
        interval : TimeInterval
            Time interval to be checked

        Returns
        -------
        bool
            True if check interval intersects with the reference interval,
            False otherwise
        """
        intersection = self._interval.intersection(interval._interval)

        if intersection.empty:
            # There is absolutely no intersection
            return False

        if intersection.upper.isCloseTo(intersection.lower, _EPS_TIME):
            # intersection below tolerance - practically empty intersection
            return False
        else:
            # see what the underlying function says
            return self._interval.overlaps(interval._interval)

    def intersect(self, interval):
        """
        Intersection operator for a time interval and this time interval.

        Returns a new interval that is the Intersection of two intervals,
        or None if there is no intersection.

        Parameters
        ----------
        interval : TimeInterval
            Time interval to be checked

        Returns
        -------
        TimeInterval
            A new interval that is the Intersection of two intervals,
            or `None` if there is no intersection

        """
        if self.is_intersecting(interval):
            intersection = self._interval.intersection(interval._interval)

            return _create_interval_from_portion(intersection)
        else:
            return None

    def union(self, interval):
        """
        Union operator for a time interval and this time interval.

        Returns a new interval that is the Union of two intervals,
        or None if there is no intersection.

        Parameters
        ----------
        interval : TimeInterval
            Time interval to be checked

        Returns
        -------
        TimeInterval
            A new interval that is the Union of two intervals,
            or `None` if there is no intersection

        """
        if self.is_intersecting(interval):
            union = self._interval.union(interval._interval)
            return _create_interval_from_portion(union)
        else:
            return None

    @u.wraps(None, (None, "s", "s", None, None), False)
    def expand(
        self,
        start_delta=0,
        end_delta=0,
        start_inclusive=True,
        end_inclusive=True,
    ):
        """
        Expands (or shrinks) the interval.

        Generates a new, expanded (or shrunk) `TimeInterval`, where:

        - new interval start: interval_start - start_delta
        - new interval end: interval_end + end_delta

        Negative start and/or end times are possible (to shrink the interval),
        though values ending in a negative interval will throw a `ValueError`.
        This method can be used to modify the ends of the interval (open or closed)
        as well.

        Parameters
        ----------
        start_delta : Quantity or float
            The delta time to expand the start of the interval
            (or to shrink, with negative values) [seconds]
        end_delta : Quantity or float
            The delta time to expand the end of the interval
            (or to shrink, with negative values)  [seconds]
        start_inclusive : bool
            True if the start of the new interval is inclusive (closed), False if
            exclusive (open)
        end_inclusive : bool
            True if the start of the new interval is inclusive (closed), False if
            exclusive (open)

        Returns
        -------
        TimeInterval
            A new `TimeInterval` that is the result of the requested change

        Raises
        ------
        ValueError
            Raised if the requested expansion results in a negative duration interval
        """
        start = self.start - start_delta * u.s
        end = self.end + end_delta * u.s

        duration = end - start

        if duration > _EPS_TIME:
            return TimeInterval(
                start,
                end,
                start_inclusive=start_inclusive,
                end_inclusive=end_inclusive,
            )
        else:
            raise ValueError(
                "Duration of the expanded/shrunk interval is negative or zero."
            )

    @property
    def duration(self) -> Quantity:
        """
        Computes the duration of the interval.

        Parameters
        ----------

        Returns
        -------
        Quantity
            Duration of the interval (always positive)
        """
        return self.end - self.start

    @property
    def start(self) -> AbsoluteDateExt:
        """Returns the start time of the interval."""
        return self._interval.lower

    @property
    def end(self) -> AbsoluteDateExt:
        """Returns the end time of the interval."""
        return self._interval.upper

    @property
    def is_start_inclusive(self) -> bool:
        """Returns whether the start time of the interval is inclusive."""
        return self._interval.left

    @property
    def is_end_inclusive(self) -> bool:
        """Returns whether the end time of the interval is inclusive."""
        return self._interval.right

    def __str__(self):
        txt = ""
        if self._interval.left:
            txt += "["
        else:
            txt += "("

        txt += f" {str(self._interval.lower)}"
        txt += f"  {str(self._interval.upper)} "

        if self._interval.right:
            txt += "]"
        else:
            txt += ")"

        return txt

    @property
    def p_interval(self):
        """
        Returns the underlying `Interval` object.

        .. warning:: Most users will not need to access this object. Intended for
            developer use only.
        """
        return self._interval


class TimeIntervalList:
    """
    Represent and manipulate time intervals.

    This is a thin wrapper around the :class:`portion.interval.Interval` class,
    using `AbsoluteDateExt` classes under the hood.

    `start_valid` and `end_valid` values are used to mark the start and end of this
    list of time intervals. If they are not specified, the beginning and end points
    of the list of `TimeInterval` instances are used.

    If a `valid_interval` is not specified (None), the beginning and end points
    of the `TimeInterval` are used.

    Parameters
    ----------
    intervals : list[TimeInterval] or None
        List of intervals
    valid_interval : TimeInterval
        Time interval within which this `TimeInterval` is valid
    """

    def __init__(self, intervals: list[TimeInterval], valid_interval=None):
        self._intervals: list = []

        if intervals:
            # if start_times is None, then there is no time interval defined

            # Fill the `Interval` list and merge as necessary
            p_intervals = self._to_p_intervals(intervals)

            # Fill the atomic `TimeInterval` objects using the merged list
            self._intervals = self._to_time_intervals(p_intervals)

        # Init range of validity
        self._valid_interval = self.__init_validity_rng(valid_interval)

    def __init_validity_rng(self, valid_interval=None):
        """
        Initialises the beginning and end of the range of validity.

        If a `valid_interval` is not specified, the beginning and end points
        of the `TimeInterval` are used.

        Parameters
        ----------
        valid_interval : TimeInterval
            Time interval within which this `TimeInterval` is valid

        Returns
        -------
        TimeInterval
            A new `TimeInterval` instance containing the start and end of validity
        """

        if valid_interval:
            # interval is not None
            return TimeInterval.from_interval(valid_interval)
        else:
            # Interval is None
            # No init time for validity defined, use the first interval init
            start_valid_tmp = self.get_interval(0).start
            start_inclusive = self.get_interval(0).p_interval.left

            # No end time for validity defined, use the last interval end
            end_valid_tmp = self.get_interval(-1).end
            end_inclusive = self.get_interval(0).p_interval.right

            # Generate the `TimeInterval`
            return TimeInterval(
                start_valid_tmp,
                end_valid_tmp,
                start_inclusive=start_inclusive,
                end_inclusive=end_inclusive,
            )

    def is_in_interval(self, time: "TimeStamped"):
        """
        Checks whether the requested time is within the time interval list.

        Parameters
        ----------
        time : TimeStamped
            Time to be checked

        Returns
        -------
        bool
            `True` if time is within the interval list, `False` otherwise. Also returns
            `False` if requested time is outside validity interval.
        """
        # Is time within validity interval?
        if not self.valid_interval.is_in_interval(time):
            return False

        # Are there any events that contain this time instant?
        for interval in self._intervals:
            if interval.is_in_interval(time):
                return True

        # If we are here, then no interval contains the time
        return False

    def is_intersecting(self, interval):
        """
        Checks whether the requested interval intersects (or is contained within)
        the interval list.

        Parameters
        ----------
        interval : TimeInterval
            Time interval to be checked

        Returns
        -------
        bool
            `True` if check interval intersects with the interval list,
            `False` otherwise
        """
        if len(self._intervals) == 0:
            # No interval present in the list, hence no intersection
            return False

        # While not very elegant, loop through the interval list to check
        # for intersections
        intersect_intervals = [
            interval_member
            for interval_member in self.intervals
            if interval_member.is_intersecting(interval)
        ]

        return True if len(intersect_intervals) > 0 else False

    def intersect(self, interval):
        """
        Intersection operator for a time interval and this time interval list.

        Returns a new interval that is the Intersection of the interval and
        the time interval list, or None if there is no intersection.

        Parameters
        ----------
        interval : TimeInterval
            Time interval to be checked

        Returns
        -------
        TimeInterval
           A new interval that is the Intersection of the interval and
           the time interval list, or None if there is no intersection.

        """
        if len(self.intervals) == 0:
            # No interval present in the list, hence no intersection possible
            return None

        # While not very elegant, loop through the interval list to check
        # for intersections
        intersect_intervals = [
            interval_member.intersect(interval)
            for interval_member in self.intervals
            if interval_member.is_intersecting(interval)
        ]

        if len(intersect_intervals) > 0:
            # There can be only a single intersection
            return intersect_intervals[0]
        else:
            # no intersection
            return None

    def intersect_list(self, interval_list):
        """
        Intersection operator for a time interval list and this time interval list.

        Returns a new interval list that is the Intersection of `interval_list` and
        this time interval list, or None if there is no intersection even in the
        validity intervals.

        Parameters
        ----------
        interval_list : TimeIntervalList
            Time interval list to be checked

        Returns
        -------
        TimeIntervalList
           A new interval list that is the Intersection of `interval_list` and
           this time interval list, or None if there is no intersection even in the
           validity intervals.

        """
        if not self.valid_interval.is_intersecting(interval_list.valid_interval):
            # Validity intervals do not intersect, hence no intersection possible
            return None

        common_valid_interval = self.valid_interval.intersect(
            interval_list.valid_interval
        )

        if not interval_list.intervals or not self.intervals:
            # There are no intervals to intersect in either self or the target
            # intervals, hence no intersection possible
            return TimeIntervalList(None, valid_interval=common_valid_interval)

        # Compute the portion intervals
        p_self_intervals = TimeIntervalList._to_p_intervals(self.intervals)
        p_other_intervals = TimeIntervalList._to_p_intervals(interval_list.intervals)

        # Do the Intersection
        p_final = p_self_intervals.intersection(p_other_intervals)

        return TimeIntervalList(
            self._to_time_intervals(p_final), valid_interval=common_valid_interval
        )

    def union(self, interval):
        """
        Union operator for a time interval and this time interval list.

        Returns a new interval that is the Union of the interval and
        the time interval list, or None if there is no intersection.

        Parameters
        ----------
        interval : TimeInterval
            Time interval to be checked

        Returns
        -------
        TimeInterval
           A new interval that is the Union of the interval and
           the time interval list, or None if there is no intersection.

        """
        if len(self.intervals) == 0:
            # No interval present in the list, hence no intersection possible
            return None

        # While not very elegant, loop through the interval list to check
        # for intersections
        union_intervals = [
            interval_member.union(interval)
            for interval_member in self.intervals
            if interval_member.is_intersecting(interval)
        ]

        if len(union_intervals) > 0:
            # There can be only a single intersection
            return union_intervals[0]
        else:
            # no intersection
            return None

    def union_list(self, interval_list):
        """
        Union operator for a time interval list and this time interval list.

        Returns a new interval list that is the Union of `interval_list` and
        this time interval list, or None if there is no intersection even in the
        validity intervals.

        Parameters
        ----------
        interval_list : TimeIntervalList
            Time interval list to be checked

        Returns
        -------
        TimeIntervalList
           A new interval list that is the Union of `interval_list` and
           this time interval list, or None if there is no intersection.

        """
        if not self.valid_interval.is_intersecting(interval_list.valid_interval):
            # Validity intervals do not intersect, hence no intersection possible
            return None

        common_valid_interval = self.valid_interval.intersect(
            interval_list.valid_interval
        )

        # Compute the portion intervals
        p_self_intervals = TimeIntervalList._to_p_intervals(self.intervals)
        p_other_intervals = TimeIntervalList._to_p_intervals(interval_list.intervals)

        # Do the Union
        p_union = p_self_intervals.union(p_other_intervals)

        # Reduce union to the common interval
        p_common = common_valid_interval.p_interval
        p_final = p_union.intersection(p_common)

        return TimeIntervalList(
            self._to_time_intervals(p_final), valid_interval=common_valid_interval
        )

    def invert(self):
        """
        Creates an *inverted* (or complement) copy of this time interval list, while
        keeping the same validity range.

        For example, for a single interval of `[t0, t1]` in a validity interval
        `[T0,T1]`, the inverted interval list would be `[T0,t0]` and `[t1,T1]`. If
        there are no intervals, the inverse becomes the entire validity interval.

        Parameters
        ----------

        Returns
        -------
        TimeIntervalList
            A new `TimeIntervalList` that has the same validity range but the individual
            intervals are inverted.
        """
        # Convert `TimeInterval` list to `Interval`
        p_interval = self._to_p_intervals(self._intervals)

        # Do the inversion
        p_int_inverted = ~p_interval

        # Fix the ends as necessary with validity interval
        p_validity = self._to_p_intervals(self.valid_interval)
        p_int_inverted = p_int_inverted.intersection(p_validity)

        # Generate the `TimeInterval` list
        intervals = self._to_time_intervals(p_int_inverted)

        # Create the `TimeIntervalList` object
        return TimeIntervalList(intervals, valid_interval=self.valid_interval)

    def get_interval(self, index):
        """
        Gets the time interval for the given index.

        Parameters
        ----------
        index : int
            requested index

        Returns
        -------
        TimeInterval
            `TimeInterval` corresponding to the index

        Raises
        ------
        IndexError
            Requested index is out of bounds

        """
        return self._intervals[index]

    @property
    def valid_interval(self) -> TimeInterval:
        """
        Gets the time interval of validity for the `TimeIntervalList`.
        """
        return self._valid_interval

    @property
    def intervals(self):
        """
        Gets the time intervals within this `TimeIntervalList`.
        """
        return self._intervals

    @staticmethod
    def _to_time_intervals(p_intervals):
        """
        Converts a `pint` `Interval` list to a `TimeInterval` list.

        Parameters
        ----------
        p_intervals : Interval
            List of intervals (pint Interval objects)

        Returns
        -------
        list[TimeInterval]
            `TimeInterval` object with the list of time intervals
        """
        intervals: list = []

        # Fill the atomic `TimeInterval` objects using the merged list
        for p_interval in p_intervals:
            # check for empty instances
            if not p_interval.lower.isCloseTo(p_interval.upper, _EPS_TIME):
                # duration not empty, add the interval
                intervals.append(_create_interval_from_portion(p_interval))

        return intervals

    @staticmethod
    def _to_p_intervals(intervals):
        """
        Converts a `TimeInterval` instance or a list to an `Interval` list
        (portion library objects).

        This is usually done to merge and simplify the elements of the list.

        Parameters
        ----------
        intervals : TimeInterval or list[TimeInterval]
            List of intervals

        Returns
        -------
        `Interval` object with the list of time intervals
        """
        # Fill the `Interval` list and merge as necessary
        p_intervals = p.empty()
        if isinstance(intervals, list):
            for interval in intervals:
                # make sure interval is not None
                if interval:
                    p_intervals = p_intervals.union(interval.p_interval)
        else:
            # intervals object is a single TimeInterval
            p_intervals = intervals.p_interval

        return p_intervals

    def __str__(self):
        txt = ""
        if self._intervals:
            # List not empty
            for interval in self._intervals:
                txt += str(interval) + "\n"
        else:
            txt = "Time interval list is empty."

        return txt


def _create_interval_from_portion(interval):
    """
    Create a new `TimeInterval` from a given :class:`Interval`
    instance.

    Parameters
    ----------
    interval : Interval
        input `Interval` instance

    Returns
    -------
    TimeInterval
        New `TimeInterval` instance
    """
    return TimeInterval(
        interval.lower,
        interval.upper,
        start_inclusive=interval.left,
        end_inclusive=interval.right,
    )
