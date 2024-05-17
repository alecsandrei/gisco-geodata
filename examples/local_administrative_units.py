from gisco_geodata.theme import (
    GEOPANDAS_AVAILABLE,
)
from gisco_geodata import (
    LocalAdministrativeUnits,
    set_httpx_args,
)

if GEOPANDAS_AVAILABLE:
    import matplotlib.pyplot as plt


def get_polygons():
    communes = LocalAdministrativeUnits()
    return communes.get(
        projection='4326',
        year='2016'
    )


def main():
    set_httpx_args(verify=False, timeout=10)

    gdf = get_polygons()

    if GEOPANDAS_AVAILABLE:
        gdf.plot()
        plt.show()


if __name__ == '__main__':
    main()
