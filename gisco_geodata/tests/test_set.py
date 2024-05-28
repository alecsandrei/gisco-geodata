from gisco_geodata import (
    set_semaphore_value,
    set_httpx_args,
)


def test_semaphore():
    from gisco_geodata.theme import SEMAPHORE_VALUE
    assert SEMAPHORE_VALUE == 50
    set_semaphore_value(5)
    from gisco_geodata.theme import SEMAPHORE_VALUE
    assert SEMAPHORE_VALUE == 5


def test_httpx():
    from gisco_geodata.parser import HTTPX_KWARGS
    assert HTTPX_KWARGS == {}
    set_httpx_args(verify=False)
    assert HTTPX_KWARGS == {'verify': False}
