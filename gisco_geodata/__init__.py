from __future__ import annotations

from .theme import (
    CoastalLines,
    LocalAdministrativeUnits,
    NUTS,
    Communes,
    UrbanAudit,
    Countries,
)

__version__ = '0.1.1'


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
