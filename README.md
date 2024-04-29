Can be used to download geodata from the [GISCO API](https://gisco-services.ec.europa.eu/distribution/v2/).

[currently under development, functionality is limited]

# Installation

```sh
git clone https://github.com/alecsandrei/gisco-geodata.git
cd gisco-geodata
python3 -m pip install .
```

# Requirements
- requests
- Python >= 3.9
- Optional: GeoPandas

# Example
```python
import os
from pathlib import Path

from gisco_geodata import (
    NUTS,
    Countries,
    set_requests_args
)


if __name__ == '__main__':
    out_dir = Path(
        os.path.normpath(os.path.expanduser("~/Desktop"))
    )  # Desktop path

    set_requests_args(verify=False)  # prevents SSLError in my case

    nuts = NUTS()

    nuts.download(
        file_format='shp',
        year='2021',
        spatial_type='BN',
        scale='60M',
        projection='4326',
        nuts_level='LEVL_3',
        out_dir=out_dir,
    )

    # Equivalent to the above
    datasets = nuts.get_datasets()
    datasets[-1].download(
        file_format='shp',
        spatial_type='BN',
        scale='60M',
        projection='4326',
        nuts_level='LEVL_3',
        out_dir=out_dir,
    )

    # Retrieve Country information as Polygons
    countries = Countries()

    # If you have geopandas installed, this will be a GDF.
    gdf = countries.get(
        countries=['RO', 'IT'],
        spatial_type='RG',
    )
    if not isinstance(gdf, list):
        print(gdf.head(5))
    else:
        print(gdf)

```