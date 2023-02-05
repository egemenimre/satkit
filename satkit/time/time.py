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

import portion as p
from orekit.pyhelpers import datetime_to_absolutedate
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
    def isCloseTo(self, other_date: TimeStamped, tolerance: float | Quantity) -> bool:
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
        return abs(super().durationFrom(other_date)) < tolerance

    def durationFrom(self, other: Type[AbsoluteDate]) -> Quantity:
        """This is equivalent to `self.durationFrom(otherDate)`.
        Output in seconds as a `Quantity` object."""
        return super().durationFrom(other) * u.s

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

    @overload
    @u.wraps(None, (None, "s"), False)
    def __sub__(self, dt: Quantity | float) -> "AbsoluteDateExt":
        ...

    @overload
    def __sub__(self, dt: "AbsoluteDateExt") -> Quantity:
        ...

    # This uses explicit `Union` as this scenario does not like the | operator
    @u.wraps(None, (None, "s"), False)
    def __sub__(
        self, time: Union[Quantity, float, "AbsoluteDateExt"]
    ) -> Union["AbsoluteDateExt", Quantity]:
        """Subtract a date or a duration from `self`.

        Depending on the input, this can be equivalent to:

        - `self.shiftedBy(-time)`, where output is a new `AbsoluteDateExt` object.
        - `self.durationFrom(time)`, where output is a `Quantity` object.
        """
        if isinstance(time, AbsoluteDate):
            return self.durationFrom(time)
        else:
            return self.shiftedBy(-time)

    @u.wraps(None, (None, "s"), False)
    def __add__(self, time: Quantity | float) -> "AbsoluteDateExt":
        """Add a duration to `self`.

        This is equivalent to `self.shiftedBy(time)`.
        Output is a new `AbsoluteDateExt` object."""
        return self.shiftedBy(time)
