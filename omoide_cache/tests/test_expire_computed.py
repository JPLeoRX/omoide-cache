import time
from omoide_cache.cache import Cache


def call(x: float) -> float:
    return x * x


def test_1():
    expire_period_s = 1

    # Create cache
    cache = Cache(call, expire_by_computed_duration_s=expire_period_s, debug=True)

    # Fill cache with 4 values
    cache.get([1])
    cache.get([2])
    cache.get([3])
    cache.get([4])

    # Make sure current len is 4 and all keys are present
    assert len(cache.results_map) == 4
    assert cache._build_key([1], {}) in cache.results_map
    assert cache._build_key([2], {}) in cache.results_map
    assert cache._build_key([3], {}) in cache.results_map
    assert cache._build_key([4], {}) in cache.results_map

    # Wait long enought for expiry to kick in
    time.sleep(2 * expire_period_s)

    # Make sure current len is 4 and all keys are present
    assert len(cache.results_map) == 4
    assert cache._build_key([1], {}) in cache.results_map
    assert cache._build_key([2], {}) in cache.results_map
    assert cache._build_key([3], {}) in cache.results_map
    assert cache._build_key([4], {}) in cache.results_map

    # This should remove key 1
    cache.get([3])

    # Make sure current len is 3 and all keys are present
    assert len(cache.results_map) == 3
    assert cache._build_key([2], {}) in cache.results_map
    assert cache._build_key([3], {}) in cache.results_map
    assert cache._build_key([4], {}) in cache.results_map

test_1()