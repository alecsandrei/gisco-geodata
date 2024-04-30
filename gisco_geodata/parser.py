from urllib.parse import urljoin
from typing import Any

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


def get_themes() -> JSON:
    resp = httpx.get(THEMES_URL, **HTTPX_KWARGS)
    resp.raise_for_status()
    return resp.json()


def get_datasets(theme: str) -> JSON:
    resp = httpx.get(DATASET_URL.format(theme=theme), **HTTPX_KWARGS)
    resp.raise_for_status()
    return resp.json()


def get_property(theme: str, property: str) -> Any:
    return get_themes()[theme][property]


async def get_file(theme: str, file_format: str, file: str) -> bytes:
    async with httpx.AsyncClient(**HTTPX_KWARGS) as client:
        resp = await client.get(
            FILE_URL.format(theme=theme, file_format=file_format, file=file)
        )
        resp.raise_for_status()
        return resp.content


async def get_param(
    theme: str,
    *params: str,
) -> JSON:
    async with httpx.AsyncClient(**HTTPX_KWARGS) as client:
        # print(PARAMS_URL.format(theme=theme, params='/'.join(params)))
        resp = await client.get(
            PARAMS_URL.format(theme=theme, params='/'.join(params)),
            follow_redirects=True
        )
        resp.raise_for_status()
        return resp.json()
