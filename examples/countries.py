from gisco_geodata.theme import GEOPANDAS_AVAILABLE
from gisco_geodata import Countries, set_httpx_args

if GEOPANDAS_AVAILABLE:
    import matplotlib.pyplot as plt


def get_countries_subset():
    """Choose two countries."""
    countries = Countries()
    return countries.get(
        spatial_type='LB',
        countries=['IT', 'RO'],
        projection='4326',
        year='2020',
    )


def get_countries_polygons_1():
    """Get all countries."""
    countries = Countries()
    return countries.get(
        spatial_type='RG', projection='4326', scale='20M', year='2020'
    )


def get_countries_points():
    """Get all countries."""
    countries = Countries()
    return countries.get(spatial_type='LB', projection='4326', year='2020')


def get_countries_polygons_2():
    countries = Countries()
    return countries.get(spatial_type='RG', year='2020')


def main():
    set_httpx_args(verify=False, timeout=10)

    gdf = get_countries_polygons_1()
    _ = get_countries_polygons_2()
    _ = get_countries_points()
    _ = get_countries_subset()

    if GEOPANDAS_AVAILABLE:
        gdf.plot()
        plt.show()


if __name__ == '__main__':
    main()
