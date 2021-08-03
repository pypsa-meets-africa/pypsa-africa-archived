# import
import logging
import os
import shutil
import zipfile
from itertools import takewhile
from operator import attrgetter

# IMPORTANT: RUN SCRIPT FROM THIS SCRIPTS DIRECTORY i.e data_exploration/ TODO: make more robust
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import fiona
import geopandas as gpd
import numpy as np
import rasterio
import requests
from _helpers import _sets_path_to_root
from _helpers import _three_2_two_digits_country
from _helpers import _two_2_three_digits_country
from _helpers import configure_logging
#from iso_country_codes import AFRICA_CC
from rasterio.mask import mask
from shapely.geometry import LineString
from shapely.geometry import MultiPolygon
from shapely.geometry import Point
from shapely.geometry import Polygon
from shapely.ops import cascaded_union

# import sys

# from ..scripts.iso_country_codes import AFRICA_CC

logger = logging.getLogger(__name__)
_sets_path_to_root("scripts")


def download_GADM(country_code, update=False):
    """
    Download gpkg file from GADM for a given country code

    Parameters
    ----------
    country_code : str
        Two letter country codes of the downloaded files
    update : bool
        Update = true, forces re-download of files

    Returns
    -------
    gpkg file per country

    """

    GADM_filename = f"gadm36_{_two_2_three_digits_country(country_code)}"
    GADM_url = f"https://biogeo.ucdavis.edu/data/gadm3.6/gpkg/{GADM_filename}_gpkg.zip"

    GADM_inputfile_zip = os.path.join(
        os.path.dirname(os.getcwd()),
        "data",
        "raw",
        "gadm",
        GADM_filename,
        GADM_filename + ".zip",
    )  # Input filepath zip

    GADM_inputfile_gpkg = os.path.join(
        os.path.dirname(os.getcwd()),
        "data",
        "raw",
        "gadm",
        GADM_filename,
        GADM_filename + ".gpkg",
    )  # Input filepath gpkg

    if not os.path.exists(GADM_inputfile_gpkg) or update is True:
        print(
            f"{GADM_filename} does not exist, downloading to {GADM_inputfile_zip}"
        )
        #  create data/osm directory
        os.makedirs(os.path.dirname(GADM_inputfile_zip), exist_ok=True)

        with requests.get(GADM_url, stream=True) as r:
            with open(GADM_inputfile_zip, "wb") as f:
                shutil.copyfileobj(r.raw, f)

        with zipfile.ZipFile(GADM_inputfile_zip, "r") as zip_ref:
            zip_ref.extractall(os.path.dirname(GADM_inputfile_zip))

    return GADM_inputfile_gpkg, GADM_filename


def get_GADM_layer(country_list, layer_id, update=False):
    """
    Function to retrive a specific layer id of a geopackage for a selection of countries
    """

    # initialization of the geoDataFrame
    geodf_GADM = gpd.GeoDataFrame()

    for country_code in country_list:
        # download file gpkg
        file_gpkg, name_file = download_GADM(country_code, False)

        # get layers of a geopackage
        list_layers = fiona.listlayers(file_gpkg)

        # get layer name
        code_layer = np.mod(layer_id, len(list_layers))
        layer_name = f"gadm36_{_two_2_three_digits_country(country_code).upper()}_{code_layer}"

        # read gpkg file
        geodf_temp = gpd.read_file(file_gpkg, layer=layer_name)

        # convert country name representation of the main country (GID_0 column)
        geodf_temp["GID_0"] = [
            _three_2_two_digits_country(twoD_c)
            for twoD_c in geodf_temp["GID_0"]
        ]

        # create a subindex column that is useful
        # in the GADM processing of sub-national zones
        geodf_temp["GADM_ID"] = geodf_temp[f"GID_{code_layer}"]

        # append geodataframes
        geodf_GADM = geodf_GADM.append(geodf_temp)

    geodf_GADM.reset_index(drop=True, inplace=True)

    return geodf_GADM


def _simplify_polys(polys, minarea=0.1, tolerance=0.01, filterremote=True):
    "Function to simplify the shape polygons"
    if isinstance(polys, MultiPolygon):
        polys = sorted(polys, key=attrgetter("area"), reverse=True)
        mainpoly = polys[0]
        mainlength = np.sqrt(mainpoly.area / (2.0 * np.pi))
        if mainpoly.area > minarea:
            polys = MultiPolygon([
                p for p in takewhile(lambda p: p.area > minarea, polys)
                if not filterremote or (mainpoly.distance(p) < mainlength)
            ])
        else:
            polys = mainpoly
    return polys.simplify(tolerance=tolerance)


def countries(update=False):
    countries = snakemake.config["countries"]

    # download data if needed and get the layer id 0, corresponding to the countries
    df_countries = get_GADM_layer(countries, 0, update)

    # select and rename columns
    df_countries = df_countries[["GID_0", "geometry"]].copy()
    df_countries.rename(columns={"GID_0": "name"}, inplace=True)

    # set index and simplify polygons
    ret_df = df_countries.set_index("name")["geometry"].map(_simplify_polys)

    return ret_df


def country_cover(country_shapes, eez_shapes=None):
    shapes = list(country_shapes)
    if eez_shapes is not None:
        shapes += list(eez_shapes)

    europe_shape = cascaded_union(shapes)
    if isinstance(europe_shape, MultiPolygon):
        europe_shape = max(europe_shape, key=attrgetter("area"))
    return Polygon(shell=europe_shape.exterior)


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


def load_EEZ(selected_countries_codes, name_file="eez_v11.gpkg"):
    EEZ_gpkg = os.path.join(os.path.dirname(os.getcwd()), "data", "raw", "eez",
                            name_file)  # Input filepath gpkg

    if not os.path.exists(EEZ_gpkg):
        raise Exception(
            f"File EEZ {name_file} not found, please download it from https://www.marineregions.org/download_file.php?name=World_EEZ_v11_20191118_gpkg.zip and copy it in {os.path.dirname(EEZ_gpkg)}"
        )

    geodf_EEZ = gpd.read_file(EEZ_gpkg)
    geodf_EEZ.dropna(axis=0, how="any", subset=["ISO_TER1"], inplace=True)
    # [["ISO_TER1", "TERRITORY1", "ISO_SOV1", "ISO_SOV2", "ISO_SOV3", "geometry"]]
    geodf_EEZ = geodf_EEZ[["ISO_TER1", "geometry"]]
    selected_countries_codes_3D = [_two_2_three_digits_country(x) for x in selected_countries_codes]
    geodf_EEZ = geodf_EEZ[[
        any([x in selected_countries_codes_3D])
        for x in geodf_EEZ["ISO_TER1"]
    ]]
    geodf_EEZ["ISO_TER1"] = geodf_EEZ["ISO_TER1"].map(lambda x: _three_2_two_digits_country(x))
    geodf_EEZ.reset_index(drop=True, inplace=True)

    geodf_EEZ.rename(columns={"ISO_TER1": "name"}, inplace=True)

    return geodf_EEZ


def eez(country_shapes, update=False, tol=1e-3):
    countries = snakemake.config["countries"]

    # load data
    df_eez = load_EEZ(countries)

    # set index and simplify polygons
    ret_df = df_eez.set_index("name").geometry.map(
        lambda x: _simplify_polys(x, filterremote=False))
    
    ret_df = gpd.GeoSeries({
        k: v
        for k, v in ret_df.iteritems() if v.distance(country_shapes[k]) < tol
    })
    ret_df.index.name = "name"

    return ret_df


def download_WorldPop(country_code, year=2020, update=False, out_logging=True, size_min=300):
    """
    Download tiff file for each country code

    Parameters
    ----------
    country_code : str
        Two letter country codes of the downloaded files.
        Files downloaded from https://data.worldpop.org/ datasets WorldPop UN adjusted
    year : int
        Year of the data to download
    update : bool
        Update = true, forces re-download of files
    size_min : int
        Minimum size of each file to download

    Returns
    -------
    WorldPop_inputfile : str
        Path of the file
    WorldPop_filename : str
        Name of the file

    """

    # UN not adjusted
    # WorldPop_filename = f"{_two_2_three_digits_country(country_code).lower()}_ppp_{year}_constrained.tif"
    # WorldPop_url = f"https://data.worldpop.org/GIS/Population/Global_2000_2020_Constrained/2020/BSGM/{_two_2_three_digits_country(country_code).upper()}/{WorldPop_filename}"

    WorldPop_filename = f"{_two_2_three_digits_country(country_code).lower()}_ppp_{year}_UNadj_constrained.tif"
    # Urls used to possibly download the file
    WorldPop_urls = [
        f"https://data.worldpop.org/GIS/Population/Global_2000_2020_Constrained/2020/BSGM/{_two_2_three_digits_country(country_code).upper()}/{WorldPop_filename}",
        f"https://data.worldpop.org/GIS/Population/Global_2000_2020_Constrained/2020/maxar_v1/{_two_2_three_digits_country(country_code).upper()}/{WorldPop_filename}"
    ]

    WorldPop_inputfile = os.path.join(os.path.dirname(os.getcwd()), "data",
                                      "raw", "WorldPop",
                                      WorldPop_filename)  # Input filepath zip

    if not os.path.exists(WorldPop_inputfile) or update is True:
        if out_logging:
            print(
                f"{WorldPop_filename} does not exist, downloading to {WorldPop_inputfile}"
            )
        #  create data/osm directory
        os.makedirs(os.path.dirname(WorldPop_inputfile), exist_ok=True)

        loaded = False
        for WorldPop_url in WorldPop_urls:
            with requests.get(WorldPop_url, stream=True) as r:
                with open(WorldPop_inputfile, "wb") as f:
                    if float(r.headers["Content-length"]) > size_min:
                        shutil.copyfileobj(r.raw, f)
                        loaded = True
                        break
        if not loaded:
            print(f"Impossible to download {WorldPop_filename}")

    return WorldPop_inputfile, WorldPop_filename


def add_population_data(df_gadm, country_codes, year=2020, out_logging=False):
    """Function to add the population info for each country shape in the gadm dataset"""
    # initialize new population column
    df_gadm["pop"] = 0

    for c_code in country_codes:
        WorldPop_inputfile, WorldPop_filename = download_WorldPop(
            c_code, 2020, update=False, out_logging=False)

        with rasterio.open(WorldPop_inputfile) as src:
            country_rows = df_gadm.loc[df_gadm["country"] == c_code]

            for index, row in country_rows.iterrows():
                # select the desired area of the raster corresponding to each polygon
                out_image, out_transform = mask(src,
                                                row["geometry"],
                                                all_touched=True,
                                                invert=False,
                                                nodata=0.0)

                # calculate total population in the selected geometry
                pop_by_geom = sum(sum(out_image[0]))

                if out_logging == True:
                    print(index, " out of ", country_rows.shape[0])

                # update the population data in the dataset
                df_gadm.loc[index, "pop"] = pop_by_geom


def gadm(update=False, year=2020):
    countries = snakemake.config["countries"]

    # download data if needed and get the last layer id [-1], corresponding to the highest resolution
    df_gadm = get_GADM_layer(countries, -1, update)

    # select and rename columns
    df_gadm.rename(columns={"GID_0": "country"}, inplace=True)

    # drop useless columns
    df_gadm = df_gadm[["country", "GADM_ID", "geometry"]]

    # add the population data to the dataset
    add_population_data(df_gadm, countries, year)

    # set index and simplify polygons
    df_gadm.set_index("GADM_ID", inplace=True)
    df_gadm["geometry"] = df_gadm["geometry"].map(_simplify_polys)

    # df = gpd.read_file(snakemake.input.nuts3)
    # df = df.loc[df['STAT_LEVL_'] == 3]
    # df['geometry'] = df['geometry'].map(_simplify_polys)
    # df = df.rename(columns={'NUTS_ID': 'id'})[['id', 'geometry']].set_index('id')

    # pop = pd.read_table(snakemake.input.nuts3pop, na_values=[':'], delimiter=' ?\t', engine='python')
    # pop = (pop
    #        .set_index(pd.MultiIndex.from_tuples(pop.pop('unit,geo\\time').str.split(','))).loc['THS']
    #        .applymap(lambda x: pd.to_numeric(x, errors='coerce'))
    #        .fillna(method='bfill', axis=1))['2014']

    # gdp = pd.read_table(snakemake.input.nuts3gdp, na_values=[':'], delimiter=' ?\t', engine='python')
    # gdp = (gdp
    #        .set_index(pd.MultiIndex.from_tuples(gdp.pop('unit,geo\\time').str.split(','))).loc['EUR_HAB']
    #        .applymap(lambda x: pd.to_numeric(x, errors='coerce'))
    #        .fillna(method='bfill', axis=1))['2014']

    # cantons = pd.read_csv(snakemake.input.ch_cantons)
    # cantons = cantons.set_index(cantons['HASC'].str[3:])['NUTS']
    # cantons = cantons.str.pad(5, side='right', fillchar='0')

    # swiss = pd.read_excel(snakemake.input.ch_popgdp, skiprows=3, index_col=0)
    # swiss.columns = swiss.columns.to_series().map(cantons)

    # pop = pop.append(pd.to_numeric(swiss.loc['Residents in 1000', 'CH040':]))
    # gdp = gdp.append(pd.to_numeric(swiss.loc['Gross domestic product per capita in Swiss francs', 'CH040':]))

    # df = df.join(pd.DataFrame(dict(pop=pop, gdp=gdp)))

    # df['country'] = df.index.to_series().str[:2].replace(dict(UK='GB', EL='GR'))

    # excludenuts = pd.Index(('FRA10', 'FRA20', 'FRA30', 'FRA40', 'FRA50',
    #                         'PT200', 'PT300',
    #                         'ES707', 'ES703', 'ES704','ES705', 'ES706', 'ES708', 'ES709',
    #                         'FI2', 'FR9'))
    # excludecountry = pd.Index(('MT', 'TR', 'LI', 'IS', 'CY', 'KV'))

    # df = df.loc[df.index.difference(excludenuts)]
    # df = df.loc[~df.country.isin(excludecountry)]

    # manual = gpd.GeoDataFrame(
    #     [['BA1', 'BA', 3871.],
    #      ['RS1', 'RS', 7210.],
    #      ['AL1', 'AL', 2893.]],
    #     columns=['NUTS_ID', 'country', 'pop']
    # ).set_index('NUTS_ID')
    # manual['geometry'] = manual['country'].map(country_shapes)
    # manual = manual.dropna()

    # df = df.append(manual, sort=False)

    # df.loc['ME000', 'pop'] = 650.

    return df_gadm


if __name__ == "__main__":
    # print(os.path.dirname(os.path.abspath(__file__)))
    if "snakemake" not in globals():
        from _helpers import mock_snakemake

        snakemake = mock_snakemake("build_shapes")
    configure_logging(snakemake)

    out = snakemake.output

    # print(snakemake.config)

    country_shapes = countries()
    save_to_geojson(country_shapes, out.country_shapes)

    offshore_shapes = eez(country_shapes)
    save_to_geojson(offshore_shapes, out.offshore_shapes)

    africa_shape = country_cover(country_shapes, offshore_shapes)
    save_to_geojson(gpd.GeoSeries(africa_shape), out.africa_shape)

    gadm_shapes = gadm()
    save_to_geojson(gadm_shapes, out.gadm_shapes)
