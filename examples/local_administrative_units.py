from gisco_geodata.theme import (
    GEOPANDAS_AVAILABLE,
)
import os
from pathlib import Path

from gisco_geodata import (
    LocalAdministrativeUnits,
    set_httpx_args,
)

if GEOPANDAS_AVAILABLE:
    import matplotlib.pyplot as plt


OUT_DIR = Path(
    os.path.normpath(os.path.expanduser("~/Desktop"))
)  # Desktop path


def get_gdf():
    communes = LocalAdministrativeUnits()
    return communes.download(
        file_format='geojson',
        spatial_type='RG',
        scale='01M',
        projection='4326',
    )


def get():
    communes = LocalAdministrativeUnits()
    return communes.download(
        out_dir=OUT_DIR,
        file_format='shp',
        scale='01M',
        spatial_type='RG',
        projection='4326',
        year='2016'
    )


def main():
    set_httpx_args(verify=False, timeout=10)

    get()
    gdf = get_gdf()

    if GEOPANDAS_AVAILABLE:
        gdf.plot()
        plt.show()


if __name__ == '__main__':
    main()
