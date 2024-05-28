from gisco_geodata.theme import GEOPANDAS_AVAILABLE
from gisco_geodata import (
    NUTS,
    set_httpx_args
)

if GEOPANDAS_AVAILABLE:
    import matplotlib.pyplot as plt


def get_countries_subset():
    """Choose two countries."""
    nuts = NUTS()
    return nuts.get(
        countries=['IT', 'RO'],
        projection='4326',
        scale='20M',
        nuts_level='LEVL_0'
    )


def get_countries_polygons():
    """Get all countries."""
    nuts = NUTS()
    return nuts.get(
        spatial_type='RG',
        projection='4326',
        scale='20M',
        nuts_level='LEVL_0'
    )


def get_countries_points():
    """Get all countries."""
    nuts = NUTS()
    return nuts.get(
        spatial_type='LB',
        projection='4326',
        nuts_level='LEVL_0'
    )


def get_regions_polygons():
    nuts = NUTS()
    return nuts.get(
        spatial_type='RG',
        nuts_level='LEVL_1',
    )


def main():
    set_httpx_args(verify=False, timeout=10)

    nuts_1 = get_regions_polygons()
    _ = get_countries_subset()
    _ = get_countries_points()
    _ = get_countries_polygons()

    if GEOPANDAS_AVAILABLE:
        nuts_1.plot()
        plt.show()


if __name__ == '__main__':
    main()
