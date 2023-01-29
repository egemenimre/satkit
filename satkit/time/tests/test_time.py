# satkit: Satellite Mission Analysis and Design for Python
#
# Copyright (C) 2023 Egemen Imre
#
# Licensed under GNU GPL v3.0. See LICENSE.rst for more info.
"""
Time functions tests.

"""

from org.orekit.time import TimeScalesFactory

from satkit import u
from satkit.time.time import AbsoluteDateExt


def test_time_sort():
    """Tests the `AbsoluteDateExt` time list sort."""
    date1 = AbsoluteDateExt(2020, 7, 11, 00, 0, 0.0, TimeScalesFactory.getUTC())
    date2 = date1.shiftedBy(-240.0)  # normal float
    date3 = date1.shiftedBy(+4 * u.min)  # Quantity
    date4 = date1.shiftedBy(+120)  # int

    sorted_list = sorted([date1, date2, date3, date4])
    # print(sorted_list)

    assert str(sorted_list[0].getDate()) == "2020-07-10T23:56:00.000Z"
    assert str(sorted_list[1].getDate()) == "2020-07-11T00:00:00.000Z"
    assert str(sorted_list[-1].getDate()) == "2020-07-11T00:04:00.000Z"


def test_time_add_sub():
    """Tests the `AbsoluteDateExt` time addition and subtraction operands."""
    date1 = AbsoluteDateExt(2020, 7, 11, 00, 0, 0.0, TimeScalesFactory.getUTC())
    dt2 = -240.0  # normal float
    dt3 = +4 * u.min  # Quantity
    dt4 = +120  # int
    date2_add = date1 + dt2
    date3_add = date1 + dt3
    date4_add = date1 + dt4

    dt2_sub = date2_add - date1
    dt3_sub = date3_add - date1
    dt4_sub = date4_add - date1

    assert str(date2_add.getDate()) == "2020-07-10T23:56:00.000Z"
    assert str(date3_add.getDate()) == "2020-07-11T00:04:00.000Z"
    assert str(date4_add.getDate()) == "2020-07-11T00:02:00.000Z"

    assert dt2_sub == -240.0 * u.second
    assert dt3_sub == 240.0 * u.second
    assert dt4_sub == 120.0 * u.second
