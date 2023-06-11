---
myst:
  substitutions:
    gnd_at_night_detector: "[`GroundAtNightDetector`](https://www.orekit.org/site-orekit-development/apidocs/org/orekit/propagation/events/GroundAtNightDetector)"
    elev_detector: "[`ElevationDetector`](https://www.orekit.org/site-orekit-development/apidocs/org/orekit/propagation/events/ElevationDetector)"
    elev_mask: "[`ElevationMask`](https://www.orekit.org/site-orekit-development/apidocs/org/orekit/utils/ElevationMask)"
    eclipse_detector: "[`GroundAtNightDetector`](https://www.orekit.org/site-orekit-development/apidocs/org/orekit/propagation/events/EclipseDetector)"
---

# Finding Events and Intervals

## Introduction

A common family of problems in satellite mission analysis involves finding *events* and *intervals* such as finding the communication times of a satellite with a groundstation, satellite eclipse entrance and exit times or finding the exact time a satellite crosses the Equator. They require the precise calculation of the time when a calculated value (or its derivative) crosses a certain threshold.

Orekit provides a powerful infrastructure to find these events, by defining a function and computing the time of the extrema or the "zero crossings" of this function. However, a higher level functionality that simply finds the intervals between these events is not featured; one can easily find the sunrise and sunset times, but the definition of "daytime or nighttime intervals" require more work. `satkit` introduces this high level functionality for some common tasks.

Furthermore, once these intervals are found (as {py:class}`.TimeInterval` objects), operations like intersection or union can be carried out with other such objects. For example, the communications times of a satellite and daytime intervals can be intersected to compute the "daytime communications opportunities". 

## Finding Ground Events and Intervals

(eventfinders/gnd_to_sat_los)=
### Ground-to-Satellite Communication (or Line-of-Sight) Intervals

The "line-of-sight intervals" from a ground location to a satellite (or any object on a predefined trajectory) is a very common problem, from satellite sighting to groundstation communication times. The {py:meth}`~satkit.events.eventfinders.gnd_pass_finder` method provided by `satkit` makes it easy to compute these "ground passes". This method uses the Orekit {{elev_detector}} event detector.

It receives the following inputs: 
- a ground location (a Geodetic Point or a Topocentric Frame), as well as a planet where this Geodetic Point is located (not needed if a Topocentric Frame is provided)
  - a search interval
- a propagator for the flying object that spans the search interval
- an elevation mask (a fixed angle value or an Orekit {{elev_mask}} object)
- a refraction model

It yields the output of intervals and maximum elevation times for these intervals.

```
intervals, max_elev_times = gnd_pass_finder(search_interval, gnd_location, elevation, propagator, planet=earth, refraction_model=refraction_model)
```

The defaults are for planet Earth (see below for the definition) and no atmospheric refraction, ideal for communications and basic optical applications. It should be noted that, while other effects like light time delay (or signal propagation delay) are not taken into account, this level of precision is not required to find the relevant intervals.   

(eventfinders/default_earth)=
```
itrf = FramesFactory.getITRF(IERSConventions.IERS_2010, True)
earth = OneAxisEllipsoid(Constants.WGS84_EARTH_EQUATORIAL_RADIUS,
                         Constants.WGS84_EARTH_FLATTENING,
                         itrf)
```

Many applications however require many more parameters out of this analysis. To compute the intervals is not enough, the maximum elevation during the pass as well as a tabulated list of azimuth and elevations are required for both satellite communications and satellite optical tracking applications. In this case, rather than this simplistic function we should use an object-oriented interface. The {py:class}`~satkit.events.gnd_access.GroundPassList` object is generated with similar inputs, and it does call the {py:meth}`~satkit.events.eventfinders.gnd_pass_finder` as above. But it also computes azimuth-elevation-range and other parameters, and bundles them into individual {py:class}`~satkit.events.gnd_access.GroundPass` objects. The {py:class}`~satkit.events.gnd_access.GroundPassList` object stores the pass intervals for convenience (as it is a {py:class}`.TimeInterval` object with the associated functionality) as well as the {py:class}`~satkit.events.gnd_access.GroundPass` objects that store the pass interval, maximum elevation time and the corresponding azimuth-elevation and range values, as well as the azimuth-elevation-range list given as a list of {py:class}`~satkit.utils.utilities.AzElRng` objects.


### Ground Illumination Intervals

Ground illumination intervals are similar to the Satellite-to-Ground Line-of-Sight intervals, except the "satellite", or the flying object that has a trajectory is actually the Sun. The {py:meth}`~satkit.events.eventfinders.gnd_illum_finder` method provides an easy interface to find the ground illumination times. This method uses the Orekit {{gnd_at_night_detector}} event detector.

The method receives the following inputs: 
- a ground location (a Geodetic Point or a Topocentric Frame), as well as a planet where this Geodetic Point is located (not needed if a Topocentric Frame is provided, see above for the [default Earth](#eventfinders/default_earth) definition)
- a search interval
- a sun {{pv_coords_provider}} (if `None`, a standard one will be generated)
- a dawn/dusk elevation mask (angle value or from the {py:class}`.StandardDawnDuskElevs` enumerator)
- a refraction model

```
intervals = gnd_illum_finder(search_interval, gnd_location, dawn_dusk_elev, sun_coords=None, planet=earth, refraction_model=refraction_model)
```

As can be seen, the inputs are very similar to the {py:meth}`~satkit.events.eventfinders.gnd_pass_finder` method. One subtle difference is that, Orekit does not provide a {{propagator}} interface for the Sun, therefore an Orekit {{ephemeris}} propagator (using 5 data points) is initialised under the hood, sampling Sun positions every 10 minutes.

The dawn/dask elevation angle can be set to zero for horizon, but usually standard definitions like Civil or Nautical Dawn/Dusk Elevation Angles (-6 and -12 degrees, respectively) are used. They are given in the {py:class}`.StandardDawnDuskElevs` enumerator for convenience. For applications with visual observations, typically Astronomical Dawn/Dask (-18 degrees) is used, to ensure that the sky is dark enough. For these cases, ITU 453 refraction model should be preferred, as the other refraction models may not deal with negative elevations well.

## Finding Satellite Events and Intervals

### Satellite Illumination Intervals

Satellite illumination intervals are defined as the durations where the satellite (or any point object on a trajectory) is outside umbra or penumbra of an occulting object (e.g., the Earth or the Moon). The {py:meth}`~satkit.events.eventfinders.sat_illum_finder` method provides an easy interface to find the satellite illumination times. This method uses the Orekit {{eclipse_detector}} event detector.

The method receives the following inputs:
- a search interval
- a propagator for the flying object that spans the search interval
- a sun {{pv_coords_provider}} (if `None`, a standard one will be generated)
- an occulting body or planet (e.g., the Earth)
- an angular margin added to the eclipse detection
- a flag to define umbra or penumbra entry/exit

```
intervals = sat_illum_finder(search_interval, propagator, use_total_eclipse=True, sun_coords=None, planet=earth)
```

For the simplest case of a satellite eclipse due to the Earth, the search interval and the satellite propagator inputs are adequate. The `planet` parameter can be replaced by the Moon defined as a `OneAxisEllipsoid`, to find the eclipse events due to the Moon (for example on the GEO satellites). The satellite illumination durations can be intersected with the "ground at night" and "ground-to satellite line-of-sight" durations to find the times, where the satellite is visible to an observer on the ground. 