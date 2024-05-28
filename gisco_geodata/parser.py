from urllib.parse import urljoin
from typing import Any
from functools import lru_cache

import httpx
from cache import AsyncLRU


URL = 'https://gisco-services.ec.europa.eu/distribution/v2/'
THEMES_URL = urljoin(URL, 'themes.json')
DATASET_URL = urljoin(URL, '{theme}/datasets.json')
PARAMS_URL = urljoin(URL, '{theme}/{params}')
FILE_URL = urljoin(URL, '{theme}/{file_format}/{file}')

HTTPX_KWARGS = {}
JSON = dict[str, Any]


@lru_cache
def get_themes() -> JSON:
    resp = httpx.get(THEMES_URL, **HTTPX_KWARGS)
    resp.raise_for_status()
    return resp.json()


@lru_cache
def get_datasets(theme: str) -> JSON:
    resp = httpx.get(DATASET_URL.format(theme=theme), **HTTPX_KWARGS)
    resp.raise_for_status()
    return resp.json()


@lru_cache
def get_property(theme: str, property: str) -> Any:
    return get_themes()[theme][property]


@AsyncLRU()
async def get_file(theme: str, file_format: str, file: str) -> bytes:
    async with httpx.AsyncClient(**HTTPX_KWARGS) as client:
        resp = await client.get(
            FILE_URL.format(theme=theme, file_format=file_format, file=file)
        )
        resp.raise_for_status()
        return resp.content


@AsyncLRU()
async def get_param(
    theme: str,
    *params: str,
) -> JSON:
    async with httpx.AsyncClient(**HTTPX_KWARGS) as client:
        resp = await client.get(
            PARAMS_URL.format(theme=theme, params='/'.join(params)),
            follow_redirects=True
        )
        resp.raise_for_status()
        return resp.json()
