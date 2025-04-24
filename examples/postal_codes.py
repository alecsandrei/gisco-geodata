import os
from pathlib import Path

from gisco_geodata import (
    PostalCodes,
    set_httpx_args,
)
from gisco_geodata.theme import GEOPANDAS_AVAILABLE

if GEOPANDAS_AVAILABLE:
    import matplotlib.pyplot as plt


OUT_DIR = Path(
    os.path.normpath(os.path.expanduser('~/Desktop'))
)  # Desktop path


def get_gdf():
    # Get as GeoJSON/Geodataframe.
    postal_codes = PostalCodes()
    return postal_codes.download(
        spatial_type='PT', projection='4326', file_format='geojson'
    )


def get_country_ids():
    postal_codes = PostalCodes()
    return postal_codes.country_ids('2020')


def get():
    # Download at out_dir
    postal_codes = PostalCodes()
    return postal_codes.download(
        out_dir=OUT_DIR,
        spatial_type='PT',
        file_format='shp',
        projection='4326',
    )


def main():
    set_httpx_args(verify=False, timeout=10)

    get()
    gdf = get_gdf()

    if GEOPANDAS_AVAILABLE:
        gdf.plot()
        plt.show()
    print(get_country_ids())


if __name__ == '__main__':
    main()
