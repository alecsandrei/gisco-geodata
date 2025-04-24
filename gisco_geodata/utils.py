from __future__ import annotations

import asyncio
<<<<<<< HEAD
import functools
=======
<<<<<<< Updated upstream
=======
import functools
import importlib.util
import os
import threading
import time
>>>>>>> Stashed changes
from collections.abc import (
    Coroutine,
    Sequence,
    Callable,
    Iterator,
)
>>>>>>> 0649080 (add github publish yml)
import importlib.util
import threading
import time
from collections.abc import (
    Callable,
    Coroutine,
    Iterator,
    Sequence,
)
from typing import (
    TYPE_CHECKING,
    Any,
    Type,
    TypeVar,
    cast,
)

import httpx

if TYPE_CHECKING:
    import geopandas as gpd

    from gisco_geodata.theme import GeoJSON

T = TypeVar('T')


def is_pytest_running():
    return 'PYTEST_CURRENT_TEST' in os.environ


def is_package_installed(name: str) -> bool:
    try:
        importlib.util.find_spec(name)
        return True
    except ImportError:
        return False


def geopandas_is_available() -> bool:
    return is_package_installed('geopandas')


def pandas_is_available() -> bool:
    return is_package_installed('pandas')


def gdf_from_geojson(geojsons: GeoJSON | Sequence[GeoJSON]) -> gpd.GeoDataFrame:
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
            crs=geojsons['crs']['properties']['name'],
        )
    elif isinstance(geojsons, Sequence):
        return cast(
            gpd.GeoDataFrame,
            pd.concat(
                [
                    gpd.GeoDataFrame.from_features(
                        features=geojson['features'],
                        crs=geojson['crs']['properties']['name'],
                    )
                    for geojson in geojsons
                ]
            ),
        )
    else:
        raise ValueError(f'Wrong argument {geojsons}')


async def handle_completed_requests(
    coros: Iterator[asyncio.futures.Future[T]],
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


def async_retry(
    on: Type[Exception] = Exception, retries: int = 50, delay: float = 0.5
):
    """Wraps async functions into try/except blocks.

    Args:
        retries: The number of retries.
        delay: The time delay in seconds between each retry.
    """

    def decorator(
        func: Callable[..., Coroutine[Any, Any, T]],
    ) -> Callable[..., Coroutine[Any, Any, T]]:
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
                f'Function {func.__name__} failed after {retries} retries.'
            )

        return wrapper

    return decorator


def retry(
    on: Type[Exception] = Exception, retries: int = 50, delay: float = 0.5
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
                f'Function {func.__name__} failed after {retries} retries.'
            )

        return wrapper

    return decorator


class RunThread(threading.Thread):
    def __init__(self, coro: Coroutine[Any, Any, T]):
        self.coro = coro
        self.result = None
        super().__init__()

    def run(self):
        self.result = asyncio.run(self.coro)


def run_async(coro: Coroutine[Any, Any, T]) -> T:
    """Function to use instead of asyncio.run.

    This prevents problems when there is already
      asynchronous code running.
      See: https://stackoverflow.com/a/75094151

    Args:
        coro (Coroutine[Any, Any, _T]):
            A coroutine object.

    Returns:
        _T: The returned result from the coroutine execution.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        thread = RunThread(coro)
        thread.start()
        thread.join()
        return cast(T, thread.result)
    else:
        return asyncio.run(coro)
