# Project Details

## Current Status

Current functionality:

- Loading a list of TLEs from file and filtering them for various parameters
- Initialise TLEs for common orbits (Sun-synchronous and geostationary)
- Adding further functionalities to basic Orekit classes like `AbsoluteDate` or `TLE`
- Good infrastructure for time interval management
- Harnessing the extensive [Orekit](https://www.orekit.org) functionalities (e.g., propagating orbits or finding events)

## What's New?

Check the [Changelog page](changelog.md) for the changelog and recently added functionalities.

## Future Functionality

1. Operations support

   a) Groundstation communication times

   b) Target imaging times

2. Satellite orbit design and analysis

   a) Repeating orbits

   b) Analysis of deviations from the ideal orbits

3. Orbit change

   a) Manoeuvres and Delta-V calculations

   b) Multiple steps

4. Satellite design

   a) Power generation with solar arrays

   b) Power consumption and battery sizing

   c) Propellant budget

## License

This project is Copyright (c) Egemen Imre and licensed under the terms of the GNU GPL v3+ licence.

## About the Author

My name is [Egemen Imre](https://twitter.com/uyducusirin), the author of satkit. While this project has really been yet another excuse to learn Python for me, for more than 20 years I have been developing Orbital Mechanics software professionally for topics ranging from satellite mission analysis and design, to actual satellite operations.

## Acknowledgements

The folks at CS deserve praise for the excellent open-source [Orekit](https://www.orekit.org) orbital mechanics library written in Java. While the interface is occasionally mind-boggling, the breadth of functions is simply amazing. Petrus Hyvönen has been maintaining the [Orekit Python Wrapper](https://gitlab.orekit.org/orekit-labs/python-wrapper), which opened the doors of Orekit to Python.
