# Working with Multiple TLEs

## Lists of Mixed TLEs: {py:class}`.TleStorage`

Many applications require working with TLEs from a number of satellites (for example satellites from the same launch or belonging to the same constellation). `satkit` enables loading and flexible filtering of such TLE lists using the {py:class}`.TleStorage` class. A fully functional example of these functionalities can be found in the [tutorials](../../tutorials).

A {py:class}`.TleStorage` object can be initialised either from a file ({py:meth}`.TleStorage.from_path`) or a string ({py:meth}`.TleStorage.from_string`) containing a list of TLE data. The third option is to initialise the storage object using another TLE list, which is shallow copied into the object.

```
# init from file
tle_storage_1 = TleStorage.from_path(tle_file_path)

# init from string
tle_storage_2 = TleStorage.from_string(tle_source_str)

# init from other TLE list
tle_storage_3 = TleStorage(tle_storage_2.tle_list)

```
Note that, the contents of the {py:class}`.TleStorage` object are stored in a list called `tle_list`. 

(tle_storage/filtering)=
## Extracting Specific Data from the Lists (Filtering)

The {py:class}`.TleStorage` object offers a number of filtering options:
- filtering by value: look for a match to a specific value
- filtering by range: look for a range of values
- filtering by function: look for matches or range of values with a custom function

"Filtering by value" is useful to match a specific identifier in the list, for example a satellite ID number or, satellites from a certain launch. The enumerator {py:class}`.TleValueFilterParams` is used to identify the parameter to be matched.
```
filtered_list_1 = tle_storage_1.filter_by_value(TleValueFilterParams.SAT_NR, 46495)
```
"Filtering by range" is useful to match a range of satellites in the list, for example satellites below a certain eccentricity threshold or between certain epoch limits. The enumerator {py:class}`.TleRangeFilterParams` is used to identify the range to be matched. This enumerator and its values are different from {py:class}`.TleValueFilterParams`, as float-like parameters cannot be exactly matched reliably. 
```
threshold_time = AbsoluteDate("2021-02-01T00:00:00.000", TimeScalesFactory.getUTC())
filtered_list_2 = tle_storage_2.filter_by_range(TleRangeFilterParams.EPOCH, min_value=threshold_time)
```
Range filtering can accept a minimum (`min_value`), a maximum (`max_value`) or both, such that:

    max_value > param > min_value

or, including the bounds:

    max_value >= param >= min_value

depending on the `includes_bounds` boolean flag.

Continuing with the example above, we can illustrate a few other "filtering by range" examples:

```
# filtering with a max and min epoch date
min_threshold_time = AbsoluteDate("2021-03-29T00:00:00.000", TimeScalesFactory.getUTC())
max_threshold_time = AbsoluteDate("2021-03-29T13:00:00.000", TimeScalesFactory.getUTC())
filtered_list_3 = tle_storage_2.filter_by_range(TleRangeFilterParams.EPOCH, min_value=min_threshold_time, max_value=max_threshold_time)

# filtering with a min inclination
min_inclination = 90 * u.deg
filtered_list_4 = tle_storage_2.filter_by_range(TleRangeFilterParams.INCLINATION, min_value=min_inclination)

# filtering with a max eccentricity
max_e = 0.001
filtered_list_5 = tle_storage_2.filter_by_range(TleRangeFilterParams.E, max_value=max_e)
```

One important thing to note is that, the filtering value can be given as a `Quantity` class (of the `pint` package) i.e., with a unit. While the code can accept inputs without units, then the inputs will be assumed to have a specific default unit. For example the default unit for inclination is radians (see enumerator {py:class}`TleDefaultUnits` for the full set of units). This helps with the all too common interfacing and unit specification errors.

The second thing to note is that the resulting filtered list is another `TleStorage` object, with its internal `tle_list` backed by the source object. In other words, the filtering does not create new TLE objects. Clearly, if the backing list is somehow changed, then all the other filtered lists may change as well.

Finally, if the filter results in an empty list, then a new `TleStorage` object is still returned, with an empty internal `tle_list`.

The third method to filter the TLEs is through custom functions. In `filter_by_func`, a user-defined function takes the TLE, runs some test and returns `True` or `False` accordingly. For example, while TLE does not have a direct way to filter for semimajor axis, a filter can be easily written with this method (see {py:class}`.TLEUtils` class API or its [description](orbits_utils.md)).

```
# define the filter function and filter the list
def sma_filter(tle):
    """Semimajor axis filter min/max."""
    return True if 7100 * u.km > TLEUtils.compute_sma(tle) > 7000 * u.km else False

filtered_list_sma_1 = tle_storage_1.filter_by_func(sma_filter)
```

The filters can be chained to generate a more complex filtering function. For example the following filters for the satellites with the number "46495" and then by a minimum TLE epoch, to create a list of the TLEs of a specific satellite after a certain epoch.

```
threshold_time = AbsoluteDate("2021-02-01T00:00:00.000", TimeScalesFactory.getUTC())
filtered_list_1 = tle_storage_1.filter_by_value(TleValueFilterParams.SAT_NR, 46495).filter_by_range(TleRangeFilterParams.EPOCH, min_value=threshold_time)
```


## Lists of TLEs of the Same Satellite: {py:class}`.TleTimeSeries`

A specific class {py:class}`.TleTimeSeries` exists to store the multiple TLEs from a single satellite with time ordering (epoch values). This is particularly useful to plot the orbit or to feed it to a propagator to propagate the satellite orbit through multiple TLEs. 

One simple way to initialise this object is to generate a `TleStorage` object and the use the special `to_tle_timeseries` method to filter a single satellite. The code below initialises a `TleStorage` from a file and filters for the satellites with the catalogue number `28366`. It is also possible to initialise a {py:class}`.TleTimeSeries` object through a list of TLE data.

```
# Initialise through filtering 
tle_timeseries_1 = TleStorage.from_path(file_path).to_tle_timeseries(28366)

# Initialise through TLE data
tle_timeseries_1 = TleTimeSeries(tle_storage_1.tle_list, 28366)
```

The `TleTimeSeries` has all the filtering features of the {py:class}`.TleStorage`, as described in the [TLE filtering section](tle_storage/filtering). 




