from __future__ import annotations

from .theme import (
    NUTS,
    CoastalLines,
    Communes,
    Countries,
    LocalAdministrativeUnits,
    PostalCodes,
    UrbanAudit,
)

__version__ = '0.1.3'

__all__ = [
    'NUTS',
    'CoastalLines',
    'Communes',
    'Countries',
    'LocalAdministrativeUnits',
    'PostalCodes',
    'UrbanAudit',
]


def set_semaphore_value(value: int):
    """The maximum number of asynchronous API calls."""
    import gisco_geodata.theme

    gisco_geodata.theme.SEMAPHORE_VALUE = value


def set_httpx_args(**kwargs):
    """Additional kwargs to use for httpx."""
    import gisco_geodata.parser

    gisco_geodata.parser.HTTPX_KWARGS = {}
    for k, v in kwargs.items():
        gisco_geodata.parser.HTTPX_KWARGS[k] = v
