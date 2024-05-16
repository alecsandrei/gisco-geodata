from gisco_geodata.theme import (
    GEOPANDAS_AVAILABLE,
)
from gisco_geodata import (
    Communes,
    set_httpx_args,
)

if GEOPANDAS_AVAILABLE:
    import matplotlib.pyplot as plt


def get_lines():
    communes = Communes()
    return communes.get(
        spatial_type='BN',
        projection='4326',
        year='2004'
    )


def get_polygons():
    communes = Communes()
    return communes.get(
        spatial_type='RG',
        scale='01M',
        projection='4326',
        year='2016'
    )


def main():
    set_httpx_args(verify=False, timeout=10)

    gdf = get_polygons()
    _ = get_lines()

    if GEOPANDAS_AVAILABLE:
        gdf.plot()
        plt.show()


if __name__ == '__main__':
    main()
