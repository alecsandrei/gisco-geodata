from gisco_geodata.theme import (
    GEOPANDAS_AVAILABLE,
    Property
)
from gisco_geodata import (
    CoastalLines,
    set_httpx_args,
)

if GEOPANDAS_AVAILABLE:
    import matplotlib.pyplot as plt


def get():
    coastal_lines = CoastalLines()
    return coastal_lines.get(
        scale='20M',
        projection='4326'
    )


def main():
    set_httpx_args(verify=False, timeout=10)

    gdf = get()

    if GEOPANDAS_AVAILABLE:
        gdf.plot()
        plt.show()


if __name__ == '__main__':
    main()
