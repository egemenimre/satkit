---
myst:
  substitutions:
    portion_interval: "[`Interval`](https://github.com/AlexandreDecan/portion)"
    elev_detector: "[`ElevationDetector`](https://www.orekit.org/site-orekit-development/apidocs/org/orekit/propagation/events/ElevationDetector)"
    elev_mask: "[`ElevationMask`](https://www.orekit.org/site-orekit-development/apidocs/org/orekit/utils/ElevationMask)"
---

# Time Intervals and Time Interval Lists

## Introduction

Time intervals are critical to define the start and end of certain events such as start and end of communications with a groundstation, entering and exiting the eclipse or start and end of a thruster firing. This is particularly useful when two intervals (or sets of intervals) can be evaluated through operations such as *union* and *intersection*. This enables us to answer questions such as "What are the time intervals where thruster firings occur during communications?” (an intersection operation between 'intervals of thruster firings' and 'communications interval lists') or “When can I see a satellite at night?" (an intersection operation between intervals of 'satellite above horizon', 'sun below horizon' and 'satellite not in eclipse').

The {py:mod}`.timeinterval` module provides the basic time interval functionality with the {py:class}`.TimeInterval` class i.e., a time interval with a start and end time/date, using the {py:class}`.AbsoluteDateExt` class under the hood to represent time and {{portion_interval}} class to manage and manipulate the time intervals. A {py:class}`.TimeInterval` can interact with other intervals through {py:meth}`.TimeInterval.union` and {py:meth}`.TimeInterval.intersect` methods. They can change their size through {py:meth}`.TimeInterval.expand` and they can check whether they contain ({py:meth}`.TimeInterval.contains`) or intersect with ({py:meth}`.TimeInterval.is_intersecting`) another time interval.

A list of such time intervals constitute {py:class}`.TimeIntervalList` class. A list also has a start and end of validity. This usually marks the start and end of an analysis. For example, a communications list that is valid for one day and containing no time intervals would mean that there are no communication opportunities for that day. The list can simply be inverted ({py:meth}`.TimeIntervalList.invert`) to get a list of 'no communication duration', which would then show a list with a single {py:class}`.TimeInterval` that spans the entire duration of validity.

## Using the Basic {py:class}`.TimeInterval` Class

A {py:class}`.TimeInterval` class can be simply initialised with a start time and either with an end time or with a duration ({py:meth}`.TimeIntervalList.from_duration`). These start and end times can be retrieved by the properties {py:meth}`.TimeInterval.start` and {py:meth}`.TimeInterval.end`.

```
interval_with_end_time = TimeInterval(
    AbsoluteDateExt("2020-04-11T00:00:00.000", TimeScalesFactory.getUTC()),
    AbsoluteDateExt("2020-04-11T00:10:00.000", TimeScalesFactory.getUTC()),
)
interval_with_duration = TimeInterval.from_duration(
    AbsoluteDateExt("2020-04-11T00:00:00.000", TimeScalesFactory.getUTC()),
    10 * u.min,
)
```

Note that the duration is given in the usual `u.min` notation for the `Quantity` objects, in this case representing minutes. The resulting time intervals can be quickly shown as:

    >>> str(interval_with_end_time)
    '[ 2020-04-11T00:00:00.000Z  2020-04-11T00:10:00.000Z ]'
    >>> str(interval_with_duration)
    '[ 2020-04-11T00:00:00.000Z  2020-04-11T00:10:00.000Z ]'

The end time of the interval should be later than the start time. Otherwise, a `ValueError` will be raised.

The {py:class}`.TimeInterval` class can answer some questions:

- {py:meth}`.TimeInterval.is_in_interval`: Is a given time within this interval?
- {py:meth}`.TimeInterval.is_equal`: Is a given interval equal to this interval?
- {py:meth}`.TimeInterval.is_intersecting`: Does a given interval have an intersection with this interval?
- {py:meth}`.TimeInterval.contains`: Does a given interval contain this interval?
- {py:meth}`.TimeInterval.duration`: What is the duration of this interval?

Some examples are given below:

    >>> interval_with_end_time.is_in_interval(AbsoluteDateExt("2020-04-11T00:05:00.000", TimeScalesFactory.getUTC()))
    True
    >>> interval_with_end_time.is_equal(TimeInterval.from_duration(AbsoluteDateExt("2020-04-11T00:00:00", TimeScalesFactory.getUTC()), 600 * u.sec))
    True
    >>> interval_with_end_time.is_intersecting(TimeInterval.from_duration(AbsoluteDateExt("2020-04-11T00:05:00", TimeScalesFactory.getUTC()), 600 * u.sec))
    True
    >>> interval_with_end_time.contains(TimeInterval.from_duration(AbsoluteDateExt("2020-04-11T00:05:00", TimeScalesFactory.getUTC()), 60 * u.sec))
    True
    >>> interval_with_end_time.duration
    600.0 <Unit('second')>

The intervals can be expanded or shrunk through the {py:meth}`.TimeInterval.expand` method and defining positive or negative time `Quantity` objects to modify the start and end times of the interval.

    >>> str(interval_with_end_time)
    '[ 2020-04-11T00:00:00.000Z  2020-04-11T00:10:00.000Z ]'
    >>> expanded = interval_with_end_time.expand(start_delta= 60.0 * u.sec, end_delta=-120.0 * u.sec)
    >>> str(expanded)
    '[ 2020-04-10T23:59:00.000Z  2020-04-11T00:08:00.000Z ]'

Time intervals can be subjected to an intersection (a new `TimeInterval` that is the intersection of two intervals) or union (a new `TimeInterval` that is the union of two intervals) operator. These operators are possible only when these two intervals have some intersection - otherwise the result will be a `None`.

    >>> str(interval_with_end_time.union(expanded))
    '[ 2020-04-10T23:59:00.000Z  2020-04-11T00:10:00.000Z ]'
    >>> str(interval_with_end_time.intersect(expanded))
    '[ 2020-04-11T00:00:00.000Z  2020-04-11T00:08:00.000Z ]'

## List of time intervals: The {py:class}`.TimeIntervalList` Class

The {py:class}`.TimeIntervalList` usually will not be generated explicitly by a user, except, for example, as an external constraint such as the durations when a groundstation is not available. Usually such lists are results of certain analyses such as eclipse intervals for a location on ground or different attitude profiles for a satellite.

The {py:class}`.TimeIntervalList` class stores the {py:class}`.TimeInterval` objects as well as another `TimeInterval` to represent the bounds of the validity of this list. If this validity interval is not defined explicitly, then it is assumed to start with the beginning of the first `TimeInterval` and end with the end of the final `TimeInterval`.

Operations such as {py:meth}`.TimeIntervalList.intersection` and {py:meth}`.TimeIntervalList.union` are also possible for two `TimeIntervalList` objects. As a `TimeIntervalList` is defined for a certain validity interval, the union or intersection of two `TimeIntervalList` objects will yield another `TimeIntervalList` that is only valid for the intersection of validity of these two intervals.

Any interval within the list can be queried through {py:meth}`.TimeIntervalList.get_interval` method. Similarly, the `TimeInterval` that keeps the interval of validity can be queried through {py:meth}`.TimeIntervalList.valid_interval` property.

The `TimeIntervalList` will yield a new, inverted (or complementing) version of itself through the {py:meth}`.TimeIntervalList.invert` method. For example, for a single interval of `[t0, t1]` in a validity interval `[T0,T1]`, the inverted interval list would be `[T0,t0]` and `[t1,T1]`. If there are no intervals, the inverse becomes the entire validity interval.

A simple example can be constructed as:

    >>> interval_1= TimeInterval(
        AbsoluteDateExt("2020-04-11T00:00:00.000", TimeScalesFactory.getUTC()),
        AbsoluteDateExt("2020-04-11T00:10:00.000", TimeScalesFactory.getUTC()),
        )
    >>> interval_2= TimeInterval(
        AbsoluteDateExt("2020-04-12T00:00:00.000", TimeScalesFactory.getUTC()),
        AbsoluteDateExt("2020-04-12T00:10:00.000", TimeScalesFactory.getUTC()),
        )
    >>> interval_list = TimeIntervalList([interval_1, interval_2])
    >>> print(interval_list)
    [ 2020-04-11T00:00:00.000Z  2020-04-11T00:10:00.000Z ]
    [ 2020-04-12T00:00:00.000Z  2020-04-12T00:10:00.000Z ]



