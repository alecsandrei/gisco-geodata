import warnings
from urllib.parse import urljoin
from typing import Any
from functools import cache

from urllib3.exceptions import InsecureRequestWarning
import requests


URL = 'https://gisco-services.ec.europa.eu/distribution/v2/'
THEMES_URL = urljoin(URL, 'themes.json')
DATASET_URL = urljoin(URL, '{theme}/datasets.json')
PARAMS_URL = urljoin(URL, '{theme}/{params}')
FILE_URL = urljoin(URL, '{theme}/{file_format}/{file}')

REQUESTS_KWARGS = {}
JSON = dict[str, Any]


def set_requests_args(**kwargs):
    for k, v in kwargs.items():
        REQUESTS_KWARGS[k] = v
        if k == 'verify' and v is False:
            warnings.filterwarnings(
                action='ignore',
                category=InsecureRequestWarning
            )


@cache
def get_themes() -> JSON:
    return requests.get(THEMES_URL, **REQUESTS_KWARGS).json()


def get_datasets(theme: str) -> JSON:
    return (
        requests.get(
            DATASET_URL.format(theme=theme),
            **REQUESTS_KWARGS
        ).json()
    )


def get_property(theme: str, property: str) -> Any:
    return get_themes()[theme][property]


def get_file(theme: str, file_format: str, file: str) -> bytes:
    return (
        requests.get(
            FILE_URL.format(theme=theme, file_format=file_format, file=file),
            **REQUESTS_KWARGS
        ).content
    )


def get_param(theme: str, *params: str) -> JSON:
    print(PARAMS_URL.format(theme=theme, params='/'.join(params)))
    return (
        requests.get(
            PARAMS_URL.format(theme=theme, params='/'.join(params)),
            **REQUESTS_KWARGS
        ).json()
    )
