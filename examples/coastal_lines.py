import os
from pathlib import Path

from gisco_geodata.theme import GEOPANDAS_AVAILABLE
from gisco_geodata import (
    CoastalLines,
    set_httpx_args,
)

if GEOPANDAS_AVAILABLE:
    import matplotlib.pyplot as plt


OUT_DIR = Path(
    os.path.normpath(os.path.expanduser('~/Desktop'))
)  # Desktop path


def get_gdf():
    # Get as GeoJSON/Geodataframe.
    coastal_lines = CoastalLines()
    return coastal_lines.download(
        spatial_type='RG', scale='20M', projection='4326'
    )


def get():
    # Download at out_dir
    coastal_lines = CoastalLines()
    return coastal_lines.download(
        out_dir=OUT_DIR,
        spatial_type='RG',
        file_format='shp',
        scale='20M',
        projection='4326',
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
