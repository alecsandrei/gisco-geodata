import geopandas as gpd

from gisco_geodata import (
    Countries,
    set_requests_args
)
from gisco_geodata import theme

set_requests_args(verify=False)
COUNTRIES = Countries()


def test_get():
    setattr(theme, 'GEOPANDAS_AVAILABLE', False)
    assert isinstance(COUNTRIES.get_units(), dict)
    assert isinstance(COUNTRIES.get_units()['RO'], list)
    geojson = COUNTRIES.get(countries=['RO', 'IT'], spatial_type='RG')
    assert isinstance(geojson, list)


def test_get_geopandas():
    setattr(theme, 'GEOPANDAS_AVAILABLE', True)
    geojson = COUNTRIES.get(countries=['RO', 'IT'], spatial_type='RG')
    assert isinstance(geojson, gpd.GeoDataFrame)
