import os
from pathlib import Path

from gisco_geodata.theme import GEOPANDAS_AVAILABLE
from gisco_geodata import (
    Communes,
    set_httpx_args,
)


if GEOPANDAS_AVAILABLE:
    import matplotlib.pyplot as plt


OUT_DIR = Path(
    os.path.normpath(os.path.expanduser('~/Desktop'))
)  # Desktop path


def get_lines():
    # If out_dir is specified, the content will
    # be saved at out_dir location
    communes = Communes()
    return communes.download(
        file_format='geojson',
        out_dir=OUT_DIR,
        spatial_type='BN',
        projection='4326',
        year='2004',
    )


def get_polygons():
    # If out_dir is not specified and the file format
    # is geojson, a geodataframe or geojson dict will be returned
    communes = Communes()
    return communes.download(
        file_format='geojson',
        spatial_type='RG',
        scale='01M',
        projection='4326',
        year='2016',
    )


def main():
    set_httpx_args(verify=False, timeout=10)

    get_lines()
    polygons = get_polygons()
    if GEOPANDAS_AVAILABLE:
        polygons.plot()
        plt.show()


if __name__ == '__main__':
    main()
