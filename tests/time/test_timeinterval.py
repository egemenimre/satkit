# satkit: Satellite Mission Analysis and Design for Python
#
# Copyright (C) 2023 Egemen Imre
#
# Licensed under GNU GPL v3.0. See LICENSE.rst for more info.
"""
Time interval functions tests.

"""
import numpy as np
import pytest
from org.orekit.time import AbsoluteDate, TimeScalesFactory

from satkit import u
from satkit.time.time import AbsoluteDateExt
from satkit.time.timeinterval import _EPS_TIME, TimeInterval, TimeIntervalList


@pytest.fixture
def init_rels():
    """Generate the relationships."""

    rels = {
        "before": TimeInterval(
            AbsoluteDateExt(2020, 4, 9, 00, 0, 0.0, TimeScalesFactory.getUTC()),
            AbsoluteDateExt(2020, 4, 11, 00, 0, 0.0, TimeScalesFactory.getUTC()),
            end_inclusive=False,
        ),
        "within": TimeInterval(
            AbsoluteDate(2020, 4, 11, 00, 5, 0.0, TimeScalesFactory.getUTC()),
            AbsoluteDateExt(2020, 4, 11, 00, 8, 0.0, TimeScalesFactory.getUTC()),
        ),
        "intersect": TimeInterval(
            AbsoluteDateExt(2020, 4, 10, 00, 0, 0.0, TimeScalesFactory.getUTC()),
            AbsoluteDateExt(2020, 4, 11, 00, 8, 0.0, TimeScalesFactory.getUTC()),
        ),
        "exact": TimeInterval(
            AbsoluteDateExt(2020, 4, 11, 00, 0, 0.0, TimeScalesFactory.getUTC()),
            AbsoluteDateExt(2020, 4, 11, 00, 10, 0.0, TimeScalesFactory.getUTC()),
        ),
        "after": TimeInterval(
            AbsoluteDateExt(2020, 4, 11, 00, 10, 0.0, TimeScalesFactory.getUTC()),
            AbsoluteDateExt(2020, 4, 12, 00, 0, 0.0, TimeScalesFactory.getUTC()),
        ),
    }

    return rels


@pytest.fixture
def init_times():
    """Generates the initial times"""
    date = AbsoluteDateExt(2020, 4, 10, 00, 0, 0.0, TimeScalesFactory.getUTC())
    return [date + dt for dt in np.arange(1, 4) * u.day]


@pytest.fixture
def durations():
    """Generates the initial durations for the initial times"""
    return (np.arange(1, 4) * (600.0 * u.s)).tolist()


def test_interval_init(init_times, durations):
    """Test initialisation."""

    interval_1 = TimeInterval.from_duration(
        init_times[0],
        durations[0],
        start_inclusive=False,
    )
    interval_2 = TimeInterval.from_interval(interval_1)
    interval_3 = TimeInterval(
        interval_1.start,
        interval_1.end,
        start_inclusive=interval_1.is_start_inclusive,
        end_inclusive=interval_1.is_end_inclusive,
    )

    assert interval_1.is_equal(interval_2)
    assert interval_2.is_equal(interval_3)


def test_interval_init_with_end_times(init_times, durations):
    """Test initialisation with explicit end times."""

    end_times = init_times[0] + durations[0]

    interval = TimeInterval(init_times[0], end_times, end_inclusive=False)

    truth_txt = "[ 2020-04-11T00:00:00.000Z  2020-04-11T00:10:00.000Z )"
    assert truth_txt == str(interval)

    # Try with AbsoluteDate
    interval = TimeInterval.from_duration(
        AbsoluteDate("2020-04-13T00:00:00.000", TimeScalesFactory.getUTC()),
        5 * u.min,
    )

    truth_txt = "[ 2020-04-13T00:00:00.000Z  2020-04-13T00:05:00.000Z ]"
    assert truth_txt == str(interval)


def test_interval_init_switched_err(init_times, durations):
    """Test `init` with switched init and end times - should raise `ValueError`."""
    with pytest.raises(ValueError):
        end_times = init_times[2] + durations[2]
        TimeInterval(end_times, init_times[2])


def test_interval_init_zero_dur_err(init_times):
    """Test `init` with equal init and end times - should return None."""

    interval = TimeInterval(init_times[1], init_times[1] + 0.1 * _EPS_TIME)

    assert interval is None


def test_interval_list_init_with_durations(init_times, durations):
    """Test initialisation with durations."""

    init_intervals = []
    for i, init_time in enumerate(init_times):
        init_intervals.append(TimeInterval.from_duration(init_times[i], durations[i]))

    intervals = TimeIntervalList(init_intervals)

    truth_txt = (
        "[ 2020-04-11T00:00:00.000Z  2020-04-11T00:10:00.000Z ]\n"
        "[ 2020-04-12T00:00:00.000Z  2020-04-12T00:20:00.000Z ]\n"
        "[ 2020-04-13T00:00:00.000Z  2020-04-13T00:30:00.000Z ]\n"
    )

    assert truth_txt == str(intervals)


def test_interval_list_init_with_end_times(init_times, durations):
    """Test initialisation with explicit end times."""

    init_intervals = []
    end_times = []
    for i, init_time in enumerate(init_times):
        end_times.append(init_times[i] + durations[i])
        init_intervals.append(TimeInterval(init_times[i], end_times[i]))

    intervals = TimeIntervalList(
        init_intervals, valid_interval=TimeInterval(init_times[0], end_times[-1])
    )

    truth_txt = (
        "[ 2020-04-11T00:00:00.000Z  2020-04-11T00:10:00.000Z ]\n"
        "[ 2020-04-12T00:00:00.000Z  2020-04-12T00:20:00.000Z ]\n"
        "[ 2020-04-13T00:00:00.000Z  2020-04-13T00:30:00.000Z ]\n"
    )

    truth_validity = "[ 2020-04-11T00:00:00.000Z  2020-04-13T00:30:00.000Z ]"

    assert truth_txt == str(intervals)
    assert truth_validity == str(intervals.valid_interval)


def test_interval_list_intersection(init_times, durations):
    """Test interval intersection."""

    init_intervals = []
    for i, init_time in enumerate(init_times):
        init_intervals.append(TimeInterval.from_duration(init_times[i], durations[i]))

    intervals = TimeIntervalList(init_intervals)

    interval_full_intersect = TimeInterval.from_duration(
        AbsoluteDate("2020-04-13T00:00:00.000", TimeScalesFactory.getUTC()),
        5 * u.min,
    )
    interval_part_intersect = TimeInterval.from_duration(
        AbsoluteDateExt("2020-04-10T23:50:00.000", TimeScalesFactory.getUTC()),
        60 * u.min,
    )
    interval_no_intersect = TimeInterval.from_duration(
        AbsoluteDateExt("2020-04-11T12:00:00.000", TimeScalesFactory.getUTC()),
        5 * u.min,
    )

    # *** Test TimeIntervalList vs. TimeInterval intersection ***
    assert intervals.is_intersecting(interval_full_intersect) is True
    assert "[ 2020-04-13T00:00:00.000Z  2020-04-13T00:05:00.000Z ]" == str(
        intervals.intersect(interval_full_intersect)
    )

    assert intervals.is_intersecting(interval_part_intersect) is True
    assert "[ 2020-04-11T00:00:00.000Z  2020-04-11T00:10:00.000Z ]" == str(
        intervals.intersect(interval_part_intersect)
    )

    assert intervals.is_intersecting(interval_no_intersect) is False
    assert intervals.intersect(interval_no_intersect) is None

    # *** Test TimeIntervalList vs. TimeIntervalList intersection ***

    test_intervals = TimeIntervalList(
        [interval_full_intersect, interval_part_intersect, interval_no_intersect]
    )

    truth_txt = (
        "[ 2020-04-11T00:00:00.000Z  2020-04-11T00:10:00.000Z ]\n"
        "[ 2020-04-13T00:00:00.000Z  2020-04-13T00:05:00.000Z ]\n"
    )

    assert truth_txt == str(intervals.intersect_list(test_intervals))


def test_interval_list_union(init_times, durations):
    """Test interval union."""

    utc_scale = TimeScalesFactory.getUTC()

    init_intervals = []
    for i, init_time in enumerate(init_times):
        init_intervals.append(TimeInterval.from_duration(init_times[i], durations[i]))

    intervals = TimeIntervalList(
        init_intervals,
        valid_interval=TimeInterval(
            AbsoluteDateExt("2020-04-11T00:00:00.000", utc_scale),
            AbsoluteDateExt("2020-04-14T00:00:00.000", utc_scale),
        ),
    )

    interval_part_intersect = TimeInterval.from_duration(
        AbsoluteDateExt("2020-04-10T23:50:00.000", utc_scale), 60 * u.min
    )
    interval_no_intersect = TimeInterval.from_duration(
        AbsoluteDateExt("2020-04-11T12:00:00.000", utc_scale), 5 * u.min
    )
    interval_full_intersect = TimeInterval.from_duration(
        AbsoluteDateExt("2020-04-13T00:00:00.000", utc_scale), 5 * u.min
    )
    interval_outside = TimeInterval.from_duration(
        AbsoluteDateExt("2020-04-13T23:50:00.000", utc_scale), 15 * u.min
    )

    # *** Test TimeIntervalList vs. TimeInterval intersection ***
    assert "[ 2020-04-13T00:00:00.000Z  2020-04-13T00:30:00.000Z ]" == str(
        intervals.union(interval_full_intersect)
    )

    assert "[ 2020-04-10T23:50:00.000Z  2020-04-11T00:50:00.000Z ]" == str(
        intervals.union(interval_part_intersect)
    )

    assert intervals.union(interval_no_intersect) is None

    # *** Test TimeIntervalList vs. TimeIntervalList intersection ***

    test_intervals = TimeIntervalList(
        [
            interval_full_intersect,
            interval_part_intersect,
            interval_no_intersect,
            interval_outside,
        ]
    )

    # print(intervals.union_list(test_intervals))
    truth_txt = (
        "[ 2020-04-11T00:00:00.000Z  2020-04-11T00:50:00.000Z ]\n"
        "[ 2020-04-11T12:00:00.000Z  2020-04-11T12:05:00.000Z ]\n"
        "[ 2020-04-12T00:00:00.000Z  2020-04-12T00:20:00.000Z ]\n"
        "[ 2020-04-13T00:00:00.000Z  2020-04-13T00:30:00.000Z ]\n"
        "[ 2020-04-13T23:50:00.000Z  2020-04-14T00:00:00.000Z ]\n"
    )

    assert truth_txt == str(intervals.union_list(test_intervals))


def test_is_intersecting(init_times, durations, init_rels):
    """Test `is_intersecting` method."""

    init_intervals = []
    for i, init_time in enumerate(init_times):
        init_intervals.append(TimeInterval.from_duration(init_times[i], durations[i]))

    interval = TimeIntervalList(init_intervals).get_interval(0)

    assert interval.is_intersecting(init_rels["before"]) is False
    assert interval.is_intersecting(init_rels["within"]) is True
    assert interval.is_intersecting(init_rels["intersect"]) is True
    assert interval.is_intersecting(init_rels["exact"]) is True
    assert interval.is_intersecting(init_rels["after"]) is False


def test_contains(init_times, durations, init_rels):
    """Test `contains` method."""

    init_intervals = []
    for i, init_time in enumerate(init_times):
        init_intervals.append(TimeInterval.from_duration(init_times[i], durations[i]))

    interval = TimeIntervalList(init_intervals).get_interval(0)

    assert interval.is_intersecting(init_rels["before"]) is False
    assert interval.is_intersecting(init_rels["within"]) is True
    assert interval.is_intersecting(init_rels["intersect"]) is True
    assert interval.is_intersecting(init_rels["exact"]) is True
    assert interval.is_intersecting(init_rels["after"]) is False


def test_is_in_interval(init_times, durations):
    """Test `is_in_interval` method."""

    utc_scale = TimeScalesFactory.getUTC()

    init_intervals = []
    for i, init_time in enumerate(init_times):
        init_intervals.append(TimeInterval.from_duration(init_times[i], durations[i]))

    interval = TimeIntervalList(init_intervals).get_interval(0)

    t_before = AbsoluteDateExt("2020-04-09T00:00:00", utc_scale)
    t_eqinit = AbsoluteDateExt("2020-04-11T00:00:00", utc_scale)
    t_within = AbsoluteDateExt("2020-04-11T00:05:00", utc_scale)
    t_eqend = AbsoluteDateExt("2020-04-11T00:10:00", utc_scale)
    t_after = AbsoluteDateExt("2020-04-11T12:00:00", utc_scale)

    assert interval.is_in_interval(t_before) is False
    assert interval.is_in_interval(t_eqinit) is True
    assert interval.is_in_interval(t_within) is True
    assert interval.is_in_interval(t_eqend) is True
    assert interval.is_in_interval(t_after) is False


def test_intersect(init_times, durations, init_rels):
    """Test `intersect` method."""

    init_intervals = []
    for i, init_time in enumerate(init_times):
        init_intervals.append(TimeInterval.from_duration(init_times[i], durations[i]))

    interval = TimeIntervalList(init_intervals).get_interval(0)

    assert interval.intersect(init_rels["before"]) is None
    assert interval.intersect(init_rels["within"]).is_equal(init_rels["within"])
    assert interval.intersect(init_rels["intersect"]).is_equal(
        TimeInterval(interval.start, init_rels["intersect"].end)
    )
    assert init_rels["exact"].is_equal(interval.intersect(init_rels["exact"]))
    assert init_rels["exact"].is_equal(init_rels["intersect"]) is False
    assert interval.intersect(init_rels["after"]) is None


# TODO aşağıdakini hallet
def test_union(init_times, durations, init_rels):
    """Test `union` method."""

    init_intervals = []
    for i, init_time in enumerate(init_times):
        init_intervals.append(TimeInterval.from_duration(init_times[i], durations[i]))

    interval = TimeIntervalList(init_intervals).get_interval(0)

    assert interval.union(init_rels["before"]) is None
    assert interval.union(init_rels["within"]).is_equal(interval)
    assert interval.union(init_rels["intersect"]).is_equal(
        TimeInterval(init_rels["intersect"].start, interval.end)
    )
    assert interval.union(init_rels["exact"]).is_equal(interval)
    assert interval.union(init_rels["after"]) is None


def test_expand(init_rels):
    """Test `expand` method."""
    # Test expansion
    expanded = init_rels["within"].expand(
        start_delta=5 * 60 * u.sec,
        end_delta=2 * 60 * u.sec,
    )
    assert expanded.is_equal(init_rels["exact"])

    # Test shrinkage
    shrunk = init_rels["exact"].expand(
        start_delta=-5 * 60 * u.sec,
        end_delta=-2 * 60 * u.sec,
    )
    assert shrunk.is_equal(init_rels["within"])


def test_expand_shrink_zero(init_rels):
    """Test `expand` method with shrink to zero - should raise `ValueError`."""
    with pytest.raises(ValueError):
        # Test shrink to zero - this raises a ValueError
        init_rels["within"].expand(start_delta=-3 * u.min)


def test_expand_shrink_negative(init_rels):
    """Test `expand` method with shrink to negative - should raise `ValueError`."""
    with pytest.raises(ValueError):
        # Test a negative duration shrinkage - this raises a ValueError
        init_rels["within"].expand(
            start_delta=-5 * 60 * u.sec,
            end_delta=-5 * u.min,
        )


def test_invert(init_times, durations):
    """Test `invert` method."""

    init_intervals = []
    end_times = []
    for i, init_time in enumerate(init_times):
        end_times.append(init_times[i] + durations[i])
        init_intervals.append(TimeInterval(init_times[i], end_times[i]))

    intervals = TimeIntervalList(
        init_intervals,
        valid_interval=TimeInterval(
            init_times[0] - 1.0 * u.day, end_times[-1] + 1.0 * u.day
        ),
    )

    inverted_intervals = intervals.invert()

    # print("intervals:")
    # print(intervals)
    # print("inverted:")
    # print(inverted_intervals)
    # print("inverted validity:")
    # print(inverted_intervals.valid_interval)

    truth_txt = (
        "[ 2020-04-10T00:00:00.000Z  2020-04-11T00:00:00.000Z ]\n"
        "[ 2020-04-11T00:10:00.000Z  2020-04-12T00:00:00.000Z ]\n"
        "[ 2020-04-12T00:20:00.000Z  2020-04-13T00:00:00.000Z ]\n"
        "[ 2020-04-13T00:30:00.000Z  2020-04-14T00:30:00.000Z ]\n"
    )

    truth_validity = "[ 2020-04-10T00:00:00.000Z  2020-04-14T00:30:00.000Z ]"

    assert truth_txt == str(inverted_intervals)
    assert truth_validity == str(inverted_intervals.valid_interval)
