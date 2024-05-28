"""
To use this script you will need to also install the following packages
    - eurostat
    - geopandas
    - mapclassify
"""

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
    dataset = get_data_df(code=code)
    assert dataset is not None

    # Preprocess the dataset.
    dataset = dataset.loc[(dataset['isced11'] == 'TOTAL') & (dataset['sex'] == 'T')]  # total unemployment rate

    # Join with the geometries.
    dataset = level_2.merge(dataset, left_on='FID', right_on=r'geo\TIME_PERIOD')
    assert isinstance(dataset, gpd.GeoDataFrame)

    # Plot.
    dataset.plot(
        column='2023',
        scheme='NaturalBreaks',
        legend=True,
        edgecolor='black',
    )
    plt.title(
        'Unemployment rate by NUTS 2 regions, 2023', fontdict={'size': 15}
    )
    plt.xlim(-25, 47)
    plt.ylim(30, 75)
    plt.show()
