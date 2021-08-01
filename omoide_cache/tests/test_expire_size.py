from omoide_cache.cache import Cache, ExpireMode


def call(x: float) -> float:
    return x * x


def test_size_expire_mode_compute_time_based():
    # Create cache
    cache = Cache(call, max_allowed_size=4, size_expire_mode=ExpireMode.COMPUTED_TIME_BASED, debug=True)

    # Fill cache with 4 values
    cache.get([1])
    cache.get([2])
    cache.get([3])
    cache.get([4])

    # Make sure current len is 4
    assert len(cache.results_map) == 4

    # Simulate some cache usage, after which next candidate for expiration is key 1 (oldest to compute)
    cache.get([1])
    cache.get([1])
    cache.get([2])
    cache.get([3])
    cache.get([3])
    cache.get([4])

    # Make sure current len is 4
    assert len(cache.results_map) == 4

    # Access with next new key, now 1 should be deleted
    # Make sure 1 was deleted (re-check length and access counts)
    cache.get([5])
    assert len(cache.results_map) == 4
    assert cache._build_key([2], {}) in cache.results_map
    assert cache._build_key([3], {}) in cache.results_map
    assert cache._build_key([4], {}) in cache.results_map
    assert cache._build_key([5], {}) in cache.results_map

    # Access with next new key, now 2 should be deleted
    # Make sure 2 was deleted (re-check length and access counts)
    cache.get([6])
    assert len(cache.results_map) == 4
    assert cache._build_key([3], {}) in cache.results_map
    assert cache._build_key([4], {}) in cache.results_map
    assert cache._build_key([5], {}) in cache.results_map
    assert cache._build_key([6], {}) in cache.results_map

    # Simulate some cache usage, after which next candidate for expiration is key 3 (oldest to compute)
    cache.get([5])
    cache.get([6])
    cache.get([6])
    cache.get([3])
    cache.get([3])
    cache.get([4])
    cache.get([5])

    # Make sure current len is 4
    assert len(cache.results_map) == 4

    # Access with next new key, now 3 should be deleted
    # Make sure 2 was deleted (re-check length and access counts)
    cache.get([7])
    assert len(cache.results_map) == 4
    assert cache._build_key([4], {}) in cache.results_map
    assert cache._build_key([5], {}) in cache.results_map
    assert cache._build_key([6], {}) in cache.results_map
    assert cache._build_key([7], {}) in cache.results_map


def test_size_expire_mode_count_based():
    # Create cache
    cache = Cache(call, max_allowed_size=4, size_expire_mode=ExpireMode.ACCESS_COUNT_BASED, debug=False)

    # Fill cache with 4 values
    cache.get([1])
    cache.get([2])
    cache.get([3])
    cache.get([4])

    # Make sure current len is 4
    assert len(cache.results_map) == 4

    # Simulate some cache usage, after which next candidate for expiration is key 1
    cache.get([2])
    cache.get([2])
    cache.get([3])
    cache.get([3])
    cache.get([4])
    cache.get([4])

    # Make sure the access counts are correct
    assert cache.access_counter_map[cache._build_key([1], {})] == 1
    assert cache.access_counter_map[cache._build_key([2], {})] == 3
    assert cache.access_counter_map[cache._build_key([3], {})] == 3
    assert cache.access_counter_map[cache._build_key([4], {})] == 3

    # Access with next new key, now 1 should be deleted
    # Make sure 1 was deleted (re-check length and access counts)
    cache.get([5])
    assert len(cache.results_map) == 4
    assert cache.access_counter_map[cache._build_key([5], {})] == 1
    assert cache.access_counter_map[cache._build_key([2], {})] == 3
    assert cache.access_counter_map[cache._build_key([3], {})] == 3
    assert cache.access_counter_map[cache._build_key([4], {})] == 3

    # Access with next new key, now previous 5 should be deleted
    # Make sure 5 was deleted (re-check length and access counts)
    cache.get([6])
    assert len(cache.results_map) == 4
    assert cache.access_counter_map[cache._build_key([6], {})] == 1
    assert cache.access_counter_map[cache._build_key([2], {})] == 3
    assert cache.access_counter_map[cache._build_key([3], {})] == 3
    assert cache.access_counter_map[cache._build_key([4], {})] == 3

    # Some more accesses, now key 2 should be next for expiry
    cache.get([6])
    cache.get([6])
    cache.get([6])
    cache.get([3])
    cache.get([4])

    # Make sure the access counts are correct
    assert cache.access_counter_map[cache._build_key([6], {})] == 4
    assert cache.access_counter_map[cache._build_key([2], {})] == 3
    assert cache.access_counter_map[cache._build_key([3], {})] == 4
    assert cache.access_counter_map[cache._build_key([4], {})] == 4

    # Access with next new key, now previous 2 should be deleted
    # Make sure 2 was deleted (re-check length and access counts)
    cache.get([7])
    assert len(cache.results_map) == 4
    assert cache.access_counter_map[cache._build_key([7], {})] == 1
    assert cache.access_counter_map[cache._build_key([3], {})] == 4
    assert cache.access_counter_map[cache._build_key([4], {})] == 4
    assert cache.access_counter_map[cache._build_key([6], {})] == 4


test_size_expire_mode_compute_time_based()
test_size_expire_mode_count_based()