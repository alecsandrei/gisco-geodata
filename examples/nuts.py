
from gisco_geodata.theme import GEOPANDAS_AVAILABLE
from gisco_geodata import (
    NUTS,
    set_httpx_args
)

if GEOPANDAS_AVAILABLE:
    import matplotlib.pyplot as plt


DEFAULT = {
    'projection': '4326',
    'scale': '20M',
    'nuts_level': 'LEVL_0'
}


def get_countries_subset():
    """Choose two countries."""
    nuts = NUTS()
    return nuts.get(
        countries=['IT', 'RO'],
        **DEFAULT
    )


def get_countries_polygons():
    """Get all countries."""
    nuts = NUTS()
    return nuts.get(spatial_type='RG', **DEFAULT)


def get_countries_points():
    """Get all countries."""
    nuts = NUTS()
    return nuts.get(spatial_type='LB', **DEFAULT)


def get_regions_polygons():
    nuts = NUTS()
    return nuts.get(
        spatial_type='RG',
        nuts_level='LEVL_1'
    )


if __name__ == '__main__':
    set_httpx_args(verify=False, timeout=10)

    gdf = get_regions_polygons()

    if GEOPANDAS_AVAILABLE:
        gdf.plot()
        plt.show()
