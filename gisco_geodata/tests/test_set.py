# NOTE: consider dropping this module later on as there is
# a race condition for HTTPX_KWARGS going on (other tests
# set the arguments of HTTPX_KWARGS and the test_httpx test could
# end up up affecting them).

from gisco_geodata import (
    set_semaphore_value,
    set_httpx_args,
)


def test_semaphore():
    set_semaphore_value(10)
    from gisco_geodata.theme import SEMAPHORE_VALUE
    assert SEMAPHORE_VALUE == 10
    set_semaphore_value(5)
    from gisco_geodata.theme import SEMAPHORE_VALUE
    assert SEMAPHORE_VALUE == 5
    set_semaphore_value(50)
    from gisco_geodata.theme import SEMAPHORE_VALUE
    assert SEMAPHORE_VALUE == 50


def test_httpx():
    set_httpx_args()
    from gisco_geodata.parser import HTTPX_KWARGS
    assert HTTPX_KWARGS == {}
    set_httpx_args(verify=False)
    from gisco_geodata.parser import HTTPX_KWARGS
    assert HTTPX_KWARGS == {'verify': False}
