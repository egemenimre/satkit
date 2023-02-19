# Working with Multiple TLEs

## Lists of Mixed TLEs: {py:class}`.TleStorage`

Many applications require working with TLEs from a number of satellites (for example satellites from the same launch or belonging to the same constellation). `satkit` enables loading and flexible filtering of such TLE lists using the {py:class}`.TleStorage` class.

For this usecase, the most common application is to load a file (or a string) containing TLE data in text format and filtering satellites with a certain parameter. Note that, Orekit needs to be initialised first.

```python
from pathlib import Path

import orekit
from orekit.pyhelpers import setup_orekit_curdir

# Init Java VM
orekit.initVM()

#  Init Orekit data
orekit_data_file_path = Path("data", "orekit-data", "orekit-data-reference.zip")
setup_orekit_curdir(str(orekit_data_file_path.resolve()))

# Orekit init complete, continue with loading the TLE file.

from org.orekit.time import AbsoluteDate, TimeScalesFactory
from satkit import process_paths
from satkit.propagation.tle_list import (
    TleRangeFilterParams,
    TleStorage,
    TleValueFilterParams,
)

# use case 1, load from TLE file, filter for a certain satellite number
# ---------------------------------------------------------------------
alt_intermed_path = Path("satkit", "propagation", "tests")
mixed_tle_file_path_1 = Path("data", "tle_mixed_1.txt")

file_path = process_paths(alt_intermed_path, mixed_tle_file_path_1)

tle_storage_1 = TleStorage.from_path(file_path)

# Print the first element of the TLE file as an example
print(tle_storage_1.tle_list[0])

# filter for a specific satellite number
filtered_list_1 = tle_storage_1.filter_by_value(TleValueFilterParams.SAT_NR, 46495)

# Print the filtered element of the filtered TLE list
print(filtered_list_1.tle_list[0])

# use case 2, load from TLE string, filter for a certain epoch
# ---------------------------------------------------------------------
with open(file_path, "r") as f:
    tle_source_str = f.read()

tle_storage_2 = TleStorage.from_string(tle_source_str)

threshold_time = AbsoluteDate("2021-02-01T00:00:00.000", TimeScalesFactory.getUTC())
filtered_list_2 = tle_storage_2.filter_by_range(TleRangeFilterParams.EPOCH, min_value=threshold_time)

# Print the first element of the filtered TLE list
print(filtered_list_2.tle_list[0])

```

The example above shows a number of important functionalities. A {py:class}`.TleStorage` object can be initialised using {py:meth}`.TleStorage.from_path` method (from a TLE file) or {py:meth}`.TleStorage.from_string` method (from a string containing a list of TLEs). The latter can be useful while downloading a TLE data from a remote location without saving it to an intermediate file. The example also shows the filtering functionality, which is detailed in the next section.

## Extracting Specific Data from the Lists (Filtering)

Once initialised, the TLE list can be filtered using the enumerator {py:class}`.TleValueFilterParams` and a filtering value. Furthermore, to filter with an element like an identifier (e.g. name or catalogue number) where an exact match can be found, `filter_by_value` method should be used. In the example above, a satellite with the catalogue number "46495" is extracted from the list.

Conversely, if a range rather than an exact match is sought (e.g. semimajor axis, epoch or eccentricity), then `filter_by_range` method and the {py:class}`.TleRangeFilterParams` should be used. In the example above, a
threshold epoch is given and all TLE values after this threshold are extracted. This method can accept a minimum, a maximum or both, such that:

    max_value > param > min_value

or, including the bounds:

    max_value >= param >= min_value

depending on the `includes_bounds` boolean flag.

Continuing with the example above, we can illustrate a few other filtering examples:

```
# filtering with a max and min epoch date
min_threshold_time = AbsoluteDate("2021-03-29T00:00:00.000", TimeScalesFactory.getUTC())
max_threshold_time = AbsoluteDate("2021-03-29T13:00:00.000", TimeScalesFactory.getUTC())
filtered_list_3 = tle_storage_2.filter_by_range(TleRangeFilterParams.EPOCH, min_value=min_threshold_time, max_value=max_threshold_time)

# Print the first element of the filtered TLE list
print(filtered_list_3.tle_list[0])

from satkit import u

# filtering with a min inclination
min_inclination = 90 * u.deg
filtered_list_4 = tle_storage_2.filter_by_range(TleRangeFilterParams.INCLINATION, min_value=min_inclination)

# Print the first element of the filtered TLE list
print(filtered_list_4.tle_list[0])

# filtering with a max eccentricity
max_e = 0.001
filtered_list_5 = tle_storage_2.filter_by_range(TleRangeFilterParams.E, max_value=max_e)

# Print the first element of the filtered TLE list
print(filtered_list_5.tle_list[0])
```

One important thing to note is that, the filtering value can be given as a `pint` {py:class}`Quantity` i.e., with a unit. While the code can accept inputs without units, then the inputs will be assumed to have a specific default unit. For example the default unit for inclination is radians (see enumerator {py:class}`TleDefaultUnits` for the full set of units). This helps with the all too common interfacing and unit specification errors.

The second thing to note is that the resulting filtered list is another `TleStorage` object, with its internal `tle_list` backed by the source object. In other words, the filtering does not create new TLE objects. Clearly, if the backing list is somehow changed, then all the other filtered lists may change as well.

Finally, if the filter results in an empty list, then a new `TleStorage` object is still returned, with an empty internal `tle_list`.

In addition to the `filter_by_value` and `filter_by_range` methods, there is a third and very powerful method to filter the TLEs through user defined functions. In `filter_by_func`, a user-defined function takes the TLE, runs some test and returns `True` or `False` accordingly. For example, while TLE does not have a direct way to filter for semimajor axis, a filter can be easily written with this method.

```
from satkit.propagation.tle import TLEUtils 

# define the filter function and filter the list
def sma_filter(tle):
    """Semimajor axis filter min/max."""
    return True if 7100 * u.km > TLEUtils.compute_sma(tle) > 7000 * u.km else False


filtered_list_sma_1 = tle_storage_1.filter_by_func(sma_filter)

# Print the first element of the filtered TLE list
print(filtered_list_sma_1.tle_list[0])

```

****************** burada kaldım ************************

## Lists of TLEs of the Same Satellite: {py:class}`.TleTimeSeries`

A specific class {py:class}`.TleTimeSeries` exists to store the multiple TLEs from a single satellite with time ordering (epoch values). This is particularly useful to plot the orbit or to feed it to a propagator to propagate the satellite orbit through multiple TLEs. The ideal way to initialise it is to initialise a `TleStorage` from a file or another source and then filter for a unique satellite identifier.

The code below initialises a `TleStorage` from a file and filters for the satellites with the catalogue number `28366`.

```
from satkit.propagation.tle_list import TleTimeSeries

tle_timeseries = TleStorage.from_path(file_path).to_tle_timeseries(28366)

# Print the first element of the filtered TLE list
print(tle_timeseries.tle_list[0])
```

Further filtering is then possible using the same methods as `TleStorage` given in the [TLE Filtering](#extracting-specific-data-from-the-lists-filtering) section. For example, all the TLEs after a certain time or above a certain semimajor exis or eccentricity value can be extracted by chaining the filters.

