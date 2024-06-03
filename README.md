Can be used to download geodata from the [GISCO API](https://gisco-services.ec.europa.eu/distribution/v2/).

# Installation

## Unreleased version

```sh
git clone https://github.com/alecsandrei/gisco-geodata.git
cd gisco-geodata
python3 -m pip install .
```

## PyPI

```sh
pip install gisco-geodata
```

# Requirements
- httpx
- async-cache
- Python >= 3.9
- Optional: GeoPandas

# Examples

Also check the [examples](https://github.com/alecsandrei/gisco-geodata/tree/main/examples) folder.

```python
import os
from pathlib import Path

from gisco_geodata import (
    NUTS,
    Countries,
    set_httpx_args,
    set_semaphore_value
)


if __name__ == '__main__':
    out_dir = Path(
        os.path.normpath(os.path.expanduser("~/Desktop"))
    )  # Desktop path

    set_httpx_args(verify=False)  # prevents SSLError in my case
    set_semaphore_value(20) # the maximum number of asynchronous API calls

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

You can also use it with the [eurostat](https://pypi.org/project/eurostat/) python package.

```python
"""To use this script you will need to also install the 'eurostat' and the 'mapclassify' packages."""

from gisco_geodata import (
    NUTS,
    set_httpx_args
)
from eurostat import (
    get_data_df,
    get_toc_df,
    set_requests_args
)
import geopandas as gpd
import matplotlib.pyplot as plt


if __name__ == "__main__":
    set_httpx_args(verify=False)
    set_requests_args(verify=False)

    # Get the geometries from the gisco service.
    nuts = NUTS()
    level_2 = nuts.get(spatial_type='RG', nuts_level='LEVL_2')
    assert isinstance(level_2, gpd.GeoDataFrame)

    # Get the dataset information.
    eurostat_database = get_toc_df()
    code = eurostat_database.loc[eurostat_database['title'] == 'Unemployment rate by NUTS 2 regions', 'code'].iloc[0]
    dataset = get_data_df(code)
    assert dataset is not None

    # Preprocess the dataset.
    dataset = dataset.loc[(dataset['isced11'] == 'TOTAL') & (dataset['sex'] == 'T')]  # total unemployment rate

    # Join with the geometries.
    dataset = level_2.merge(dataset, left_on='FID', right_on=r'geo\TIME_PERIOD')
    assert isinstance(dataset, gpd.GeoDataFrame)

    # Plot.
    dataset.plot(column='2023', scheme='NaturalBreaks', legend=True, edgecolor='black',
                 title='Unemployment rate by NUTS 2 regions, 2023')
    plt.show()

```

# Disclaimer

This plugin, Eurostat Downloader, is an independent project created by Cuvuliuc Alex-Andrei. It is not an official product of Eurostat, and Cuvuliuc Alex-Andrei is not affiliated, associated, authorized, endorsed by, or in any way officially connected with Eurostat or any of its subsidiaries or its affiliates.

# Copyright notice

Before using this package, please read the information [provided by Eurostat](https://ec.europa.eu/eurostat/web/gisco/geodata).
