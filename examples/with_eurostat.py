"""
To use this script you will need to also install the following packages
    - eurostat
    - geopandas
    - mapclassify
"""

import geopandas as gpd
import matplotlib.pyplot as plt
from eurostat import get_data_df, get_toc_df, set_requests_args

from gisco_geodata import NUTS, set_httpx_args


def get_plot():
    set_httpx_args(verify=False)
    set_requests_args(verify=False)

    # Get the geometries from the gisco service.
    nuts = NUTS()
    level_2 = nuts.get(spatial_type='RG', nuts_level='LEVL_2')
    assert isinstance(level_2, gpd.GeoDataFrame)

    # Get the dataset information.
    eurostat_database = get_toc_df()
    title, code = eurostat_database.loc[
        eurostat_database['title']
        == 'Unemployment by sex, age, educational attainment level and NUTS 2 region (1 000)',
        ['title', 'code'],
    ].iloc[0]
    dataset = get_data_df(code)
    assert dataset is not None

    # Preprocess the dataset.
    dataset = dataset.loc[
        (dataset['isced11'] == 'TOTAL') & (dataset['sex'] == 'T')
    ]  # total unemployment rate
    # Join with the geometries.
    dataset = level_2.merge(
        dataset, left_on='NUTS_ID', right_on=r'geo\TIME_PERIOD'
    )
    assert isinstance(dataset, gpd.GeoDataFrame)

    # Plot.
    dataset.plot(
        column='2023', scheme='NaturalBreaks', legend=True, edgecolor='black'
    )
    plt.title(title, fontdict={'size': 15, 'wrap': True})
    plt.xlim(-25, 47)
    plt.ylim(30, 75)
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    get_plot()
