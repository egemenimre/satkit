# satkit: Satellite Mission Analysis and Design for Python
#
# Copyright (C) 2023 Egemen Imre
#
# Licensed under GNU GPL v3.0. See LICENSE.rst for more info.
"""
TLE list tests.

"""
from pathlib import Path

from orekit.pyhelpers import setup_orekit_curdir
from org.orekit.time import AbsoluteDate, TimeScalesFactory

from satkit import process_paths, u
from satkit.propagation.tle import TLEUtils
from satkit.propagation.tle_list import (
    TleRangeFilterParams,
    TleStorage,
    TleTimeSeries,
    TleValueFilterParams,
)

extra_path = Path(
    "..",
    "..",
    "..",
)

orekit_data_file_path = Path("data", "orekit-data", "orekit-data-reference.zip")

alt_intermed_path = Path("satkit", "propagation", "tests")
mixed_tle_file_path_1 = Path("data", "tle_mixed_1.txt")
time_series_tle_file_path_1 = Path("data", "tle_rasat_desc.txt")
time_series_tle_file_path_2 = Path("data", "tle_rasat.txt")
starlink_tle_file_path_1 = Path("data", "starlink_tle.txt")


def setup_module():
    """setup any state specific to the execution of the module."""

    #  Init Orekit data
    data_file = process_paths(extra_path, orekit_data_file_path).resolve()

    setup_orekit_curdir(str(data_file))


def test_parse_storage_file():
    """Test parsing of the storage file with mixed TLE input."""
    file_path = process_paths(alt_intermed_path, mixed_tle_file_path_1)

    tle_storage = TleStorage.from_path(file_path)

    truth_no_of_elements = 19
    truth_pos = 3
    # APRIZESAT 1
    truth_line1 = (
        "1 28372U 04025G   21088.15052337  .00000024  00000-0  18112-4 0  9991"
    )
    truth_line2 = (
        "2 28372  98.4324  42.3607 0046090 190.1598 169.8668 14.49665428885585"
    )

    # check number of elements
    assert len(tle_storage.tle_list) == truth_no_of_elements

    # check specific element at `truth_pos`
    assert str(tle_storage.tle_list[truth_pos]).split("\r\n")[0:3] == [
        truth_line1,
        truth_line2,
    ]


def test_filter_value():
    """Tests filtering for a value equivalence."""
    file_path = process_paths(alt_intermed_path, mixed_tle_file_path_1)

    tle_storage = TleStorage.from_path(file_path)

    filtered_list_sat_nr = tle_storage.filter_by_value(
        TleValueFilterParams.SAT_NR, 46495
    )

    empty_filtered_list = tle_storage.filter_by_value(
        TleValueFilterParams.SAT_NR, 56495
    )

    filtered_list_int_deg = (
        tle_storage.filter_by_value(TleValueFilterParams.LAUNCH_YR, 2018)
        .filter_by_value(TleValueFilterParams.LAUNCH_NR, 14)
        .filter_by_value(TleValueFilterParams.LAUNCH_PIECE, "H")
    )

    assert isinstance(filtered_list_sat_nr, TleStorage)
    assert len(filtered_list_sat_nr.tle_list) == 2
    assert len(empty_filtered_list.tle_list) == 0
    assert len(filtered_list_int_deg.tle_list) == 1


def test_filter_func():
    """Tests filtering for a value range with a function."""
    file_path = process_paths(alt_intermed_path, mixed_tle_file_path_1)

    tle_storage = TleStorage.from_path(file_path)

    def sma_filter_1(tle):
        """Semimajor axis filter min."""
        return True if TLEUtils.compute_sma(tle) > 7000 * u.km else False

    def sma_filter_2(tle):
        """Semimajor axis filter max."""
        return True if 7000 * u.km > TLEUtils.compute_sma(tle) else False

    def sma_filter_3(tle):
        """Semimajor axis filter min/max."""
        return True if 7100 * u.km > TLEUtils.compute_sma(tle) > 7000 * u.km else False

    filtered_list_sma_1 = tle_storage.filter_by_func(sma_filter_1)
    filtered_list_sma_2 = tle_storage.filter_by_func(sma_filter_2)
    filtered_list_sma_3 = tle_storage.filter_by_func(sma_filter_3)

    assert len(filtered_list_sma_1.tle_list) == 11
    assert len(filtered_list_sma_2.tle_list) == 8
    assert len(filtered_list_sma_3.tle_list) == 8


def test_filter_range():
    """Tests filtering for a value range with min/max parameters."""
    file_path = process_paths(alt_intermed_path, mixed_tle_file_path_1)

    tle_storage = TleStorage.from_path(file_path)

    filtered_list_i_1 = tle_storage.filter_by_range(
        TleRangeFilterParams.INCL, min_value=98.1 * u.deg
    )

    filtered_list_i_2 = tle_storage.filter_by_range(
        TleRangeFilterParams.INCL, max_value=98.1 * u.deg
    )

    filtered_list_i_3 = tle_storage.filter_by_range(
        TleRangeFilterParams.INCL, min_value=98.1 * u.deg, max_value=98.3 * u.deg
    )

    filtered_list_lau_yr_1 = tle_storage.filter_by_range(
        TleRangeFilterParams.LAUNCH_YR,
        min_value=2007,
        max_value=2010,
        includes_bounds=True,
    )

    # print(filtered_list_lau_yr_1.tle_list)
    # print("---->", len(filtered_list_lau_yr_1.tle_list))

    filtered_list_i_none = tle_storage.filter_by_range(TleRangeFilterParams.INCL)

    assert len(filtered_list_i_1.tle_list) == 11
    assert len(filtered_list_i_2.tle_list) == 8
    assert len(filtered_list_i_3.tle_list) == 7
    assert len(filtered_list_i_none.tle_list) == 0
    assert len(filtered_list_lau_yr_1.tle_list) == 8


def test_tle_timeseries_ordered():
    """Test parsing of the TLE Timeseries with ordered time input."""
    file_path = process_paths(alt_intermed_path, time_series_tle_file_path_2)

    tle_storage = TleStorage.from_path(file_path).to_tle_timeseries(37791)

    assert str(tle_storage.tle_list[0].getDate()) == "2021-03-15T02:02:02.753376Z"
    assert str(tle_storage.tle_list[-1].getDate()) == "2021-03-31T21:19:42.808224Z"


def test_tle_timeseries_unordered():
    """Test parsing of the TLE Timeseries with inverted time input."""
    file_path = process_paths(alt_intermed_path, time_series_tle_file_path_1)

    tle_storage = TleStorage.from_path(file_path).to_tle_timeseries(37791)

    assert str(tle_storage.tle_list[0].getDate()) == "2021-03-30T04:20:36.40416Z"
    assert str(tle_storage.tle_list[-1].getDate()) == "2021-04-01T20:16:48.785376Z"


def test_tle_timeseries_time_filter():
    """Test parsing of the TLE Timeseries with time filter."""
    file_path = process_paths(alt_intermed_path, time_series_tle_file_path_1)

    tle_storage = TleStorage.from_path(file_path).to_tle_timeseries(37791)

    threshold_time = AbsoluteDate(2021, 4, 1, 0, 0, 0.0, TimeScalesFactory.getUTC())
    tle_storage_filtered = tle_storage.filter_by_range(
        TleRangeFilterParams.EPOCH, min_value=threshold_time
    )

    # print(tle_storage_filtered.tle_list[0].getDate())
    # print(tle_storage_filtered.tle_list[-1].getDate())

    assert isinstance(tle_storage_filtered, TleTimeSeries)
    assert (
        str(tle_storage_filtered.tle_list[0].getDate()) == "2021-04-01T02:14:48.404256Z"
    )
    assert (
        str(tle_storage_filtered.tle_list[-1].getDate())
        == "2021-04-01T20:16:48.785376Z"
    )
