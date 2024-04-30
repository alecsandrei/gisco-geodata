from urllib.parse import urljoin
from typing import (
    Any,
    Optional
)
from functools import cache

import httpx


URL = 'https://gisco-services.ec.europa.eu/distribution/v2/'
THEMES_URL = urljoin(URL, 'themes.json')
DATASET_URL = urljoin(URL, '{theme}/datasets.json')
PARAMS_URL = urljoin(URL, '{theme}/{params}')
FILE_URL = urljoin(URL, '{theme}/{file_format}/{file}')

HTTPX_KWARGS = {}
JSON = dict[str, Any]


def set_httpx_args(**kwargs):
    for k, v in kwargs.items():
        HTTPX_KWARGS[k] = v


@cache
def get_themes() -> JSON:
    return httpx.get(THEMES_URL, **HTTPX_KWARGS).json()


def get_datasets(theme: str) -> JSON:
    return (
        httpx.get(
            DATASET_URL.format(theme=theme),
            **HTTPX_KWARGS
        ).json()
    )


def get_property(theme: str, property: str) -> Any:
    return get_themes()[theme][property]


def get_file(theme: str, file_format: str, file: str) -> bytes:
    return (
        httpx.get(
            FILE_URL.format(theme=theme, file_format=file_format, file=file),
            **HTTPX_KWARGS
        ).content
    )


async def get_param(
    theme: str,
    *params: str,
    client: Optional[httpx.AsyncClient] = None,
) -> JSON:
    print(PARAMS_URL.format(theme=theme, params='/'.join(params)))
    if client is None:
        client = httpx.AsyncClient(**HTTPX_KWARGS)
    resp = await client.get(
        PARAMS_URL.format(theme=theme, params='/'.join(params)),
        follow_redirects=True
    )
    resp.raise_for_status()
    return resp.json()
