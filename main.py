import os
from pathlib import Path

from gisco_geodata import (
    Theme,
    set_requests_args
)


if __name__ == '__main__':
    out_dir = Path(
        os.path.normpath(os.path.expanduser("~/Desktop"))
    )  # Desktop path

    set_requests_args(verify=False)  # prevents SSLError in my case

    Theme.NUTS.download(
        file_format='shp',
        year='2021',
        spatial_type='BN',
        scale='60M',
        projection='4326',
        nuts_level='LEVL_3',
        out_dir=out_dir,
    )
