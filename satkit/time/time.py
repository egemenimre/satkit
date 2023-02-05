# satkit: Satellite Mission Analysis and Design for Python
#
# Copyright (C) 2023 Egemen Imre
#
# Licensed under GNU GPL v3.0. See LICENSE.rst for more info.
"""
AbsoluteDate extended class.

"""
from datetime import datetime
from typing import Type, Union, overload

from org.orekit.time import AbsoluteDate, TimeStamped
from pint import Quantity

from satkit import u


class AbsoluteDateExt(AbsoluteDate):
    """
    Extends the Orekit `AbsoluteDate` class with added functionality.
    """

    def __init__(self, *args):
        """Extends the Orekit `AbsoluteDate` class with added functionality.

        Input can be an `AbsoluteDate`, `datetime` or the usual
        :class:`AbsoluteDate` initialisation options."""
        if len(args) == 1 and isinstance(args[0], AbsoluteDate):
            # This practically deep copies the input AbsoluteDate object
            super().__init__(args[0], 0.0)
        elif len(args) == 1 and isinstance(args[0], datetime):
            # This converts datetime into an input AbsoluteDate object
            super().__init__(datetime_to_absolutedate(args[0]), 0.0)
        else:
            # Generate the AbsoluteDateExt object
            super().__init__(*args)

    @u.wraps(None, (None, "s"), False)
    def shiftedBy(self, dt: float | Quantity) -> "AbsoluteDateExt":
        """
        Get a time-shifted date.

        Calling this method is equivalent to call `new AbsoluteDateExt(this, dt)`.

        Parameters
        ----------
        dt : float or Quantity
            time shift in seconds

        Returns
        -------
        new_date : AbsoluteDateExt
            a new date, shifted with respect to instance (which is immutable)

        """
        return AbsoluteDateExt(self, float(dt))

    @u.wraps(None, (None, None, "s"), False)
    def isCloseTo(self, other_date: "TimeStamped", tolerance: float | Quantity) -> bool:
        """
        Check if the instance time is close to another.

        Parameters
        ----------
        other_date : TimeStamped
            the instant to compare this date to

        tolerance : float or Quantity
            the separation, in seconds, under which the two instants will be
            considered close to each other

        Returns
        -------
        bool
            true if the duration between the instance and the argument is
            strictly below the tolerance

        """
        # durationFrom and tolerance are guaranteed to be in seconds
        return abs(self.durationFrom(other_date)) < tolerance

    def __lt__(self, other):
        if other == p.inf:
            return self.isBefore(AbsoluteDateExt.FUTURE_INFINITY)
        elif other == -p.inf:
            return self.isBefore(AbsoluteDateExt.PAST_INFINITY)
        else:
            return self.isBefore(other)

    def __le__(self, other):
        if other == p.inf:
            return self.isBeforeOrEqualTo(AbsoluteDateExt.FUTURE_INFINITY)
        elif other == -p.inf:
            return self.isBeforeOrEqualTo(AbsoluteDateExt.PAST_INFINITY)
        else:
            return self.isBeforeOrEqualTo(other)

    def __eq__(self, other):
        if other == p.inf:
            return self.isEqualTo(AbsoluteDateExt.FUTURE_INFINITY)
        elif other == -p.inf:
            return self.isEqualTo(AbsoluteDateExt.PAST_INFINITY)
        else:
            return self.isEqualTo(other)

    def __ge__(self, other):
        if other == p.inf:
            return self.isAfterOrEqualTo(AbsoluteDateExt.FUTURE_INFINITY)
        elif other == -p.inf:
            return self.isAfterOrEqualTo(AbsoluteDateExt.PAST_INFINITY)
        else:
            return self.isAfterOrEqualTo(other)

    def __gt__(self, other):
        if other == p.inf:
            return self.isAfter(AbsoluteDateExt.FUTURE_INFINITY)
        elif other == -p.inf:
            return self.isAfter(AbsoluteDateExt.PAST_INFINITY)
        else:
            return self.isAfter(other)

    def __sub__(self, other: type[AbsoluteDate]) -> Quantity:
        """This is equivalent to `self.durationFrom(otherDate)`.
        Output in seconds as a `Quantity` object."""
        return self.durationFrom(other) * u.s

    @u.wraps(None, (None, "s"), False)
    def __add__(self, dt: Quantity) -> "AbsoluteDateExt":
        """This is equivalent to `self.shiftedBy(dt)`.
        Output is a new `AbsoluteDateExt` object."""
        return self.shiftedBy(dt)
