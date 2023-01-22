# satkit: Satellite Mission Analysis and Design (based on Orekit)

[![CircleCI Status](https://img.shields.io/circleci/build/github/egemenimre/satkit/master?logo=circleci&label=CircleCI)](https://circleci.com/gh/egemenimre/satkit)
[![Codecov Status](https://codecov.io/gh/egemenimre/satkit/branch/master/graph/badge.svg)](https://codecov.io/gh/egemenimre/satkit)
[![Documentation Status](https://readthedocs.org/projects/satkit/badge/?version=latest)](https://satkit.readthedocs.io/en/latest/?badge=latest)

satkit is an open source Python package, aiming at providing an advanced functionality to solve satellite mission analysis and design as well as orbital mechanics problems with enough precision and performance to be used in the design and operation of real satellites. The target audience is academics and amateur satellite community, including Cubesats (and anyone else who might be interested). It is built on the excellent open-source [Orekit](https://www.orekit.org) library (and the [Orekit Python Wrapper](https://gitlab.orekit.org/orekit-labs/python-wrapper)), but simplifying the interfaces for common use-cases.

Currently, there is no functionality. :)

## Documentation and Examples

The documentation for satkit is here: <https://satkit.readthedocs.io/>

As a quick-start, you can find some hands-on Jupyter examples in the [tutorials directory](https://github.com/egemenimre/satkit/tree/master/docs/tutorials) (or in the [documentation](https://satkit.readthedocs.io/en/latest/tutorials.html) for a text version).


## Installing satkit

[//]: # ()
[//]: # (The satkit package is on [PyPI]&#40;https://pypi.org/project/satkit/&#41; and you can install it simply by running:)

[//]: # ()
[//]: # (    pip install satkit)

[//]: # ()
[//]: # (You can also install it via [conda-forge]&#40;https://github.com/conda-forge/satkit-feedstock&#41;:)

[//]: # ()
[//]: # (    conda install -c conda-forge satkit)

[//]: # ()
[//]: # (Do not install `satkit` using `sudo`.)


You can find the source code on GitHub: <https://github.com/egemenimre/satkit>


## Requirements

-   NumPy and SciPy are used for the underlying mathematical algorithms
-   [Orekit](https://www.orekit.org) handles the orbital mechanics computations.
-   [Orekit Python Wrapper](https://gitlab.orekit.org/orekit-labs/python-wrapper) provides a Python wrapper for Orekit.
-   [Pint](https://github.com/hgrecco/pint) provides units and quantity support.
-   [Portion](https://github.com/AlexandreDecan/portion) handles the time interval mechanics
-   Pytest provides the testing framework


## Licence

This project is Copyright (c) Egemen Imre and licensed under the terms of the GNU GPL v3+ licence.
