from __future__ import annotations

import pkg_resources
from typing import (
    TYPE_CHECKING,
    Sequence,
    Union
)

if TYPE_CHECKING:
    from gisco_geodata.theme import GeoJSON
    import geopandas as gpd


def is_package_installed(name: str) -> bool:
    try:
        pkg_resources.get_distribution(name)
        return True
    except pkg_resources.DistributionNotFound:
        return False


def geopandas_is_available() -> bool:
    return is_package_installed('geopandas')


def numbers_from(string: str) -> list[str]:
    return [char for char in string if char.isdigit()]


def from_geojson(
    geojsons: Union[GeoJSON, Sequence[GeoJSON]]
) -> gpd.GeoDataFrame:
    """Created a GeoDataFrame from GeoJSON.

    Args:
        geojsons (Union[GeoJSON, Sequence[GeoJSON]]): GeoJSON information.

    Returns:
        GeoDataFrame: The GeoDataFrame describing the GeoJSONs.
    """
    assert geopandas_is_available()

    import geopandas as gpd
    import pandas as pd

    if isinstance(geojsons, dict):
        return gpd.GeoDataFrame.from_features(
            features=geojsons['features'],
            crs=geojsons['crs']['properties']['name']
        )
    elif isinstance(geojsons, Sequence):
        return pd.concat([
            gpd.GeoDataFrame.from_features(
                features=geojson['features'],
                crs=geojson['crs']['properties']['name']
            )
            for geojson in geojsons
        ])
    else:
        raise ValueError(f'Wrong argument {geojsons}')
