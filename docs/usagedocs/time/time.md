# `AbsoluteDate` with Benefits: {py:class}`.AbsoluteDateExt`

The {py:class}`.AbsoluteDateExt` is a thin wrapper around the already powerful (but not too python friendly) Orekit {{abs_date}} class. {{abs_date}} uses the underlying Java class for its operations, but offers some useful tools like ordering help through magic classes (such as `__lt__()`, `__ge__()` etc.), overloaded plus and minus operators and time units support. It is a subclass of {{abs_date}} and does not introduce any new parameters. Therefore, it can be safely used in the Orekit functionalities.

An Orekit {{abs_date}} object can be converted to {py:class}`.AbsoluteDateExt` by simply creating a new object, that is a deep copy of the old {{abs_date}} object (in this example `abs_date`):

    abs_date_ext = AbsoluteDateExt(abs_date)

## Time Units Support

`satkit` makes extensive use of the units (thanks to [`pint`](https://pint.readthedocs.io/) package), and the {py:class}`.AbsoluteDateExt` class can easily work with units for the methods that are commonly used with {{abs_date}}. The following is an example for the {py:meth}`~satkit.time.time.AbsoluteDateExt.shiftedBy` method.

    >>> date1 = AbsoluteDateExt(2020, 7, 11, 00, 0, 0.0, TimeScalesFactory.getUTC())
    >>> date2 = date1.shiftedBy(-240.0)  # normal float (interpreted as seconds)
    >>> date3 = date1.shiftedBy(+4 * u.min)  # Quantity
    >>> date4 = date1.shiftedBy(+120)  # int

As can be seen, the “extended” version of the {{abs_date}} can now work with units (saving a lot of unnecessary conversion errors), can default to “seconds” when no unit is supplied (just like {{abs_date}} does) and, unlike {{abs_date}}, it can now handle `int` input.

Similar support exists for {py:meth}`.AbsoluteDateExt.durationFrom` and `{py:meth}.AbsoluteDateExt.isCloseTo` methods. Therefore, the output of the {py:meth}`.AbsoluteDateExt.durationFrom` is a {{pint_quantity}} object, expressing time properly with units.

## Adding and Subtracting Time

{py:class}`.AbsoluteDateExt` brings addition and subtraction support. Therefore, the following can be conveniently written, adding and subtracting durations from a date to compute another date:

    >>> date1 = AbsoluteDateExt("2020-04-13T00:00:00.000", TimeScalesFactory.getUTC())
    >>> 
    >>> date2_add = date1 + (-240.0)  # normal float
    >>> date3_add = date1 + 4 * u.min  # Quantity
    >>> date4_add = date1 + 120  # int (interpreted as seconds)
    >>> 
    >>> date2_sub = date1 - 4 * u.min  # Quantity

Continuing with the same example, a date can be subtracted from another, resulting in a duration.

    >>> dt2_sub = date2_add - date1

## Sorting Time Objects

The {py:class}`.AbsoluteDateExt` class enables sorting of lists of time objects. For example, the following generates a list of time objects and then sorts it:

    sorted_list = sorted([date1, date2, date3, date4])