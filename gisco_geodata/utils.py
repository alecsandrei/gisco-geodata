from __future__ import annotations

import asyncio
import importlib.util
import time
import functools
from typing import (
    TYPE_CHECKING,
    Sequence,
    Coroutine,
    Callable,
    Any,
    cast,
    Type,
    TypeVar,
    Iterator,
)

import httpx

if TYPE_CHECKING:
    from gisco_geodata.theme import GeoJSON
    import geopandas as gpd


def is_package_installed(name: str) -> bool:
    try:
        importlib.util.find_spec(name)
        return True
    except ImportError:
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


_T = TypeVar('_T')


async def handle_completed_requests(
    coros: Iterator[asyncio.futures.Future[_T]]
) -> list[_T]:
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


def async_retry(
    on: Type[Exception] = Exception,
    retries: int = 50,
    delay: float = 0.5
):
    """Wraps async functions into try/except blocks.

    Args:
        retries: The number of retries.
        delay: The time delay in seconds between each retry.
    """
    def decorator(
        func: Callable[..., Coroutine[Any, Any, _T]]
    ) -> Callable[..., Coroutine[Any, Any, _T]]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < retries:
                try:
                    return await func(*args, **kwargs)
                except on:
                    await asyncio.sleep(delay)
                    attempts += 1
            raise RuntimeError(
                f"Function {func.__name__} failed after {retries} retries."
            )
        return wrapper
    return decorator


def retry(
    on: Type[Exception] = Exception,
    retries: int = 50,
    delay: float = 0.5
):
    """Wraps functions into try/except blocks.

    Args:
        on: The Exception type that should be raised to retry.
        retries: The number of retries.
        delay: The time delay in seconds between each retry.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < retries:
                try:
                    return func(*args, **kwargs)
                except on:
                    time.sleep(delay)
                    attempts += 1
            raise RuntimeError(
                f"Function {func.__name__} failed after {retries} retries."
            )
        return wrapper
    return decorator
