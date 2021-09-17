# SPDX-FileCopyrightText: : 2017-2020 The PyPSA-Eur Authors
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Creates Voronoi shapes for each bus representing both onshore and offshore regions.

Relevant Settings
-----------------

.. code:: yaml

    countries:

.. seealso::
    Documentation of the configuration file ``config.yaml`` at
    :ref:`toplevel_cf`

Inputs
------

- ``resources/country_shapes.geojson``: confer :ref:`shapes`
- ``resources/offshore_shapes.geojson``: confer :ref:`shapes`
- ``networks/base.nc``: confer :ref:`base`

Outputs
-------

- ``resources/regions_onshore.geojson``:

    .. image:: ../img/regions_onshore.png
        :scale: 33 %

- ``resources/regions_offshore.geojson``:

    .. image:: ../img/regions_offshore.png
        :scale: 33 %

Description
-----------

"""

import logging
import os

import geopandas as gpd
import numpy
import pandas as pd
import pypsa
from _helpers import configure_logging
from osm_pbf_power_data_extractor import create_country_list
from vresutils.graph import voronoi_partition_pts

_logger = logging.getLogger("build_bus_regions")

# Requirement to set path to filepath for execution
# os.chdir(os.path.dirname(os.path.abspath(__file__)))


# error occurs here: ERROR:shapely.geos:IllegalArgumentException: Geometry must be a Point or LineString
def save_to_geojson(df, fn):
    if os.path.exists(fn):
        os.unlink(fn)  # remove file if it exists
    if not isinstance(df, gpd.GeoDataFrame):
        df = gpd.GeoDataFrame(dict(geometry=df))

    # save file if the GeoDataFrame is non-empty
    if df.shape[0] > 0:
        df = df.reset_index()
        schema = {**gpd.io.file.infer_schema(df), "geometry": "Unknown"}
        df.to_file(fn, driver="GeoJSON", schema=schema)
    else:
        # create empty file to avoid issues with snakemake
        with os.open(fn, "w") as fp:
            pass


def custom_voronoi_partition_pts(points, outline, add_bounds_shape=True, multiplier=5):
    """
    Compute the polygons of a voronoi partition of `points` within the
    polygon `outline`

    Attributes
    ----------
    points : Nx2 - ndarray[dtype=float]
    outline : Polygon
    no_multipolygons : bool (default: False)
        If true, replace each MultiPolygon by its largest component

    Returns
    -------
    polygons : N - ndarray[dtype=Polygon|MultiPolygon]
    """

    import numpy as np
    from scipy.spatial import Voronoi
    from shapely.geometry import Point, Polygon

    points = np.asarray(points)

    if len(points) == 1:
        polygons = [outline]
    else:

        xmin, ymin = np.amin(points, axis=0)
        xmax, ymax = np.amax(points, axis=0)

        if add_bounds_shape:
            # check bounds of the shape
            minx_o, miny_o, maxx_o, maxy_o = outline.boundary.bounds
            xmin = min(xmin, minx_o)
            ymin = min(ymin, miny_o)
            xmax = min(xmax, maxx_o)
            ymax = min(ymax, maxy_o)

        xspan = xmax - xmin
        yspan = ymax - ymin

        # to avoid any network positions outside all Voronoi cells, append
        # the corners of a rectangle framing these points
        vor = Voronoi(
            np.vstack(
                (
                    points,
                    [
                        [xmin - multiplier * xspan, ymin - multiplier * yspan],
                        [xmin - multiplier * xspan, ymax + multiplier * yspan],
                        [xmax + multiplier * xspan, ymin - multiplier * yspan],
                        [xmax + multiplier * xspan, ymax + multiplier * yspan],
                    ],
                )
            )
        )

        polygons = []
        for i in range(len(points)):
            poly = Polygon(vor.vertices[vor.regions[vor.point_region[i]]])

            if not poly.is_valid:
                poly = poly.buffer(0)

            poly = poly.intersection(outline)

            polygons.append(poly)

    polygons_arr = np.empty((len(polygons),), "object")
    polygons_arr[:] = polygons
    return polygons_arr


if __name__ == "__main__":
    if "snakemake" not in globals():
        from _helpers import mock_snakemake

        snakemake = mock_snakemake("build_bus_regions")
    configure_logging(snakemake)

    countries = create_country_list(snakemake.config["countries"])

    n = pypsa.Network(snakemake.input.base_network)

    country_shapes = gpd.read_file(snakemake.input.country_shapes).set_index("name")[
        "geometry"
    ]
    offshore_shapes = gpd.read_file(snakemake.input.offshore_shapes).set_index("name")[
        "geometry"
    ]

    # Issues in voronoi_creation due to overlapping/duplications will be removed with that function
    # First issues where observed for offshore shapes means that first country-onshore voronoi worked fine
    # TODO: Find out the root cause for this issues
    import shapely
    from shapely.geometry import JOIN_STYLE, shape
    from shapely.ops import unary_union
    from shapely.validation import make_valid

    # country_shapes = make_valid(country_shapes)
    # offshore_shapes = make_valid(offshore_shapes)

    onshore_regions = []
    offshore_regions = []

    for country in countries:

        c_b = n.buses.country == country
        # Check if lv_buses exist in onshape. TD has no buses!
        if n.buses.loc[c_b & n.buses.substation_lv, ["x", "y"]].empty:
            _logger.warning(f"No low voltage buses found for {country}!")
            continue

        # print(country)
        onshore_shape = country_shapes[country]
        # print(shapely.validation.explain_validity(onshore_shape), onshore_shape.area)
        onshore_locs = n.buses.loc[c_b & n.buses.substation_lv, ["x", "y"]]
        # print(onshore_locs.values)
        onshore_regions.append(
            gpd.GeoDataFrame(
                {
                    "name": onshore_locs.index,
                    "x": onshore_locs["x"],
                    "y": onshore_locs["y"],
                    "geometry": custom_voronoi_partition_pts(
                        onshore_locs.values, onshore_shape
                    ),
                    "country": country,
                }
            )
        )

        # These two logging could be commented out
        if country not in offshore_shapes.index:
            _logger.warning(f"No off-shore shapes for {country}")
            continue

        # Note: the off_shore shape should be present because cheched 10 lines above
        offshore_shape = offshore_shapes[country]

        if n.buses.loc[c_b & n.buses.substation_off, ["x", "y"]].empty:
            _logger.warning(f"No off-shore substations found for {country}")
            continue
        else:
            # print(offshore_shape.is_valid)
            # print(offshore_shape.is_simple)
            # print(shapely.validation.explain_validity(offshore_shape), offshore_shape.area)
            offshore_locs = n.buses.loc[c_b & n.buses.substation_off, ["x", "y"]]
            offshore_regions_c = gpd.GeoDataFrame(
                {
                    "name": offshore_locs.index,
                    "x": offshore_locs["x"],
                    "y": offshore_locs["y"],
                    "geometry": custom_voronoi_partition_pts(
                        offshore_locs.values, offshore_shape
                    ),
                    "country": country,
                }
            )
            offshore_regions_c = offshore_regions_c.loc[offshore_regions_c.area > 1e-2]
            offshore_regions.append(offshore_regions_c)

    save_to_geojson(
        pd.concat(onshore_regions, ignore_index=True), snakemake.output.regions_onshore
    )
    if len(offshore_regions) != 0:
        offshore_regions = pd.concat(offshore_regions, ignore_index=True)
    save_to_geojson(offshore_regions, snakemake.output.regions_offshore)
