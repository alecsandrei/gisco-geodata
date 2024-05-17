from gisco_geodata.theme import GEOPANDAS_AVAILABLE
from gisco_geodata import (
    UrbanAudit,
    set_httpx_args
)

if GEOPANDAS_AVAILABLE:
    import matplotlib.pyplot as plt


def get_cities():
    """Choose two countries."""
    countries = UrbanAudit()
    return countries.get(
        spatial_type='RG',
        projection='4326',
        category='C'
    )

def get_functional_urban_areas():
    """Choose two countries."""
    countries = UrbanAudit()
    return countries.get(
        spatial_type='RG',
        countries=['IT', 'RO'],
        projection='4326',
        category='F'
    )


def main():
    set_httpx_args(verify=False, timeout=10)

    gdf = get_functional_urban_areas()
    gdf = get_cities()

    if GEOPANDAS_AVAILABLE:
        gdf.plot()
        plt.show()


if __name__ == '__main__':
    main()
