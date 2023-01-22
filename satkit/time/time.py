# satkit: Satellite Mission Analysis and Design for Python
#
# Copyright (C) 2023 Egemen Imre
#
# Licensed under GNU GPL v3.0. See LICENSE.rst for more info.
"""
AbsoluteDate extended class.

"""

from org.orekit.time import AbsoluteDate
from pint import Quantity

from satkit import u


class AbsoluteDateExt(AbsoluteDate):
    """
    Extends the Orekit `AbsoluteDate` class with added functionality.
    """

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

    def __lt__(self, other):
        return self.isBefore(other)

    def __le__(self, other):
        return self.isBeforeOrEqualTo(other)

    def __eq__(self, other):
        return self.isEqualTo(other)

    def __ge__(self, other):
        return self.isAfterOrEqualTo(other)

    def __gt__(self, other):
        return self.isAfter(other)

    def __sub__(self, other: type[AbsoluteDate]) -> Quantity:
        """This is equivalent to `self.durationFrom(otherDate)`.
        Output in seconds as a `Quantity` object."""
        return self.durationFrom(other) * u.s
