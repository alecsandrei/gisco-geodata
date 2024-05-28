from .theme import (
    CoastalLines,
    LocalAdministrativeUnits,
    NUTS,
    Communes,
    UrbanAudit,
    Countries,
)


def set_semaphore_value(value: int):
    """The maximum number of asynchronous API calls."""
    import gisco_geodata.theme
    gisco_geodata.theme.SEMAPHORE_VALUE = value


def set_httpx_args(**kwargs):
    """Additional kwargs to use for httpx."""
    import gisco_geodata.parser
    for k, v in kwargs.items():
        gisco_geodata.parser.HTTPX_KWARGS[k] = v
