# User Documentation

## Initialising satkit

To be able to initialise `satkit`, Orekit and Java Virtual Machine should be initialised and the Orekit Data File (containing Earth Orientation Parameters etc.) should be loaded. If the Orekit Data File is already present, a single line with a path to this file is adequate:

    init_satkit(Path("..", "data", "orekit-data", "orekit-data-master.zip"))

However, if the data file does not exist, the `download_data_file` should be set to `True`. Then the file path becomes the destination file path for the data file. 

    init_satkit(Path("..", "data", "orekit-data", "orekit-data-master.zip"), download_data_file=True)

```{note}
After downloading the file, the `download_data_file` should be set to `False` (or deleted altogether, as it is the default setting). The archive files are not updated very frequently, and downloading the file every day will not make any difference.

If the latest files are needed for the analysis, the websites for these files can be found in the [shell script provided by Orekit](https://gitlab.orekit.org/orekit/orekit-data/-/blob/master/update.sh). 
```

The user can also search for a number of directories for the file through this {py:meth}`~satkit.init_satkit` method.

    init_satkit(Path("..", "data", "orekit-data", "orekit-data-master.zip"), other_path_dir_1, other_path_dir_2)

The search is conducted first in the main path, then inserting the other alternate path directories:

- Nominal path: `current working dir` + `filepath`
- Alternate paths: 
  - `current working dir` + `other_path_dir_1` + `filepath`
  - `current working dir` + `other_path_dir_2` + `filepath`
  - ...

## Orbits and Trajectories

```{toctree} 
---
maxdepth: 2
---
usagedocs/propagation/orbits_utils
usagedocs/propagation/tle_storage
usagedocs/events/eventfinders

```

## Working with Time and Intervals

```{toctree} 
---
maxdepth: 2
---
usagedocs/time/time
usagedocs/time/timeinterval

```



