import time
from omoide_cache.cache import Cache, RefreshMode

number_of_calls = {}
def call(x: float) -> float:
    if x in number_of_calls:
        number_of_calls[x] = number_of_calls[x] + 1
    else:
        number_of_calls[x] = 1
    return number_of_calls[x]


def test_1():
    refresh_duration_s = 1
    refresh_period_s = 3

    # Create cache
    cache = Cache(call, refresh_duration_s=refresh_duration_s, refresh_mode=RefreshMode.INDEPENDENT, refresh_period_s=refresh_period_s, debug=True)

    # Fill cache with 4 values
    cache.get([1])
    cache.get([2])
    cache.get([3])
    cache.get([4])

    # Make sure current len is 4 and all keys are present
    assert len(cache.results_map) == 4
    assert cache.results_map[(cache._build_key([1], {}))] == 1
    assert cache.results_map[(cache._build_key([2], {}))] == 1
    assert cache.results_map[(cache._build_key([3], {}))] == 1
    assert cache.results_map[(cache._build_key([4], {}))] == 1

    # Wait long enough for refresh to kick in
    time.sleep(5)

    # Make sure current len is 4 and all keys are present
    assert len(cache.results_map) == 4
    assert cache.results_map[(cache._build_key([1], {}))] == 2
    assert cache.results_map[(cache._build_key([2], {}))] == 2
    assert cache.results_map[(cache._build_key([3], {}))] == 2
    assert cache.results_map[(cache._build_key([4], {}))] == 2

    # Close the cache
    cache.terminate()


test_1()