import asyncio

import geopandas as gpd

from gisco_geodata import (
    Countries,
    NUTS,
    set_httpx_args
)
from gisco_geodata import theme

set_httpx_args(verify=False)
COUNTRIES = Countries()
NUTS_ = NUTS()


def test_get_countries():
    setattr(theme, 'GEOPANDAS_AVAILABLE', False)
    units = asyncio.run(COUNTRIES.get_units())
    assert isinstance(units, dict)
    assert isinstance(units['RO'], list)
    geojson = COUNTRIES.get(countries=['RO', 'IT'], spatial_type='RG')
    assert isinstance(geojson, list)
    for geojson_ in geojson:
        assert all(key in geojson_ for key in ['crs', 'features', 'type'])
    setattr(theme, 'GEOPANDAS_AVAILABLE', True)
    geojson = COUNTRIES.get(countries=['RO', 'IT'], spatial_type='RG')
    assert isinstance(geojson, gpd.GeoDataFrame)


def test_get_nuts():
    setattr(theme, 'GEOPANDAS_AVAILABLE', False)
    geojson = NUTS_.get(
        countries='RO',
        nuts_level='LEVL_0',
        spatial_type='RG'
    )
    assert isinstance(geojson, list)
    setattr(theme, 'GEOPANDAS_AVAILABLE', True)
    geojson = NUTS_.get(
        countries='RO',
        nuts_level='LEVL_0',
        spatial_type='RG'
    )
    assert isinstance(geojson, gpd.GeoDataFrame)
