from __future__ import annotations

import pkg_resources
from typing import (
    TYPE_CHECKING,
    Sequence,
    cast,
    TypeVar,
    Iterator,
)
import asyncio

import httpx

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


def gdf_from_geojson(
    geojsons: GeoJSON | Sequence[GeoJSON]
) -> gpd.GeoDataFrame:
    """Created a GeoDataFrame from GeoJSON.

    Args:
        geojsons (GeoJSON | Sequence[GeoJSON]): GeoJSON information.

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
        return cast(
            gpd.GeoDataFrame,
            pd.concat([
                gpd.GeoDataFrame.from_features(
                    features=geojson['features'],
                    crs=geojson['crs']['properties']['name']
                ) for geojson in geojsons
            ])
        )
    else:
        raise ValueError(f'Wrong argument {geojsons}')


T = TypeVar('T')


async def handle_completed_requests(
    coros: Iterator[asyncio.futures.Future[T]]
) -> list[T]:
    json = []
    for coro in coros:
        try:
            json.append(await coro)  # <8>
        except httpx.HTTPStatusError:
            raise
        except httpx.RequestError:
            raise
        except KeyboardInterrupt:
            break
    return json
