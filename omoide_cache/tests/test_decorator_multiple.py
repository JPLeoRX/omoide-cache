import time
from omoide_cache.cache_decorator import omoide_cache


class ExampleService:
    def __init__(self):
        self.power = 3

    @omoide_cache()
    def costly_method_1(self, number: int) -> float:
        time.sleep(0.2)
        return number * number

    @omoide_cache()
    def costly_method_2(self, number: int) -> float:
        time.sleep(0.2)
        return number ** self.power


def test_1_one_service_two_methods():
    s = ExampleService()

    # Check 1st method initial
    assert s.costly_method_1(10) == 100
    assert s.costly_method_1(20) == 400
    assert s.costly_method_1(30) == 900

    # Check 1st method cached
    assert s.costly_method_1(10) == 100
    assert s.costly_method_1(10) == 100
    assert s.costly_method_1(20) == 400
    assert s.costly_method_1(20) == 400
    assert s.costly_method_1(30) == 900
    assert s.costly_method_1(30) == 900

    # Check 2nd method initial
    assert s.costly_method_2(1) == 1
    assert s.costly_method_2(2) == 8
    assert s.costly_method_2(3) == 27

    # Check 2nd method cached
    assert s.costly_method_2(1) == 1
    assert s.costly_method_2(1) == 1
    assert s.costly_method_2(2) == 8
    assert s.costly_method_2(2) == 8
    assert s.costly_method_2(3) == 27
    assert s.costly_method_2(3) == 27

    # Make sure both caches exist
    assert '_cache_of_costly_method_1' in s.__dict__
    assert '_cache_of_costly_method_2' in s.__dict__

    # Make sure all keys exist in both caches
    cache_1 = s.__dict__['_cache_of_costly_method_1']
    cache_2 = s.__dict__['_cache_of_costly_method_2']
    assert cache_1.is_cached((s, 10)) is True
    assert cache_1.is_cached((s, 20)) is True
    assert cache_1.is_cached((s, 30)) is True
    assert cache_2.is_cached((s, 1)) is True
    assert cache_2.is_cached((s, 2)) is True
    assert cache_2.is_cached((s, 3)) is True


def test_2_two_services_one_method():
    s1 = ExampleService()
    s2 = ExampleService()

    # Check 1st service
    assert s1.costly_method_1(10) == 100
    assert s1.costly_method_1(20) == 400
    assert s1.costly_method_1(30) == 900

    # Check 1st service cached
    assert s1.costly_method_1(10) == 100
    assert s1.costly_method_1(10) == 100
    assert s1.costly_method_1(20) == 400
    assert s1.costly_method_1(20) == 400
    assert s1.costly_method_1(30) == 900
    assert s1.costly_method_1(30) == 900

    # Check 2nd service
    assert s2.costly_method_1(1) == 1
    assert s2.costly_method_1(2) == 4
    assert s2.costly_method_1(3) == 9

    # Check 2nd service cached
    assert s2.costly_method_1(1) == 1
    assert s2.costly_method_1(1) == 1
    assert s2.costly_method_1(2) == 4
    assert s2.costly_method_1(2) == 4
    assert s2.costly_method_1(3) == 9
    assert s2.costly_method_1(3) == 9

    # Make sure both caches exist
    assert '_cache_of_costly_method_1' in s1.__dict__
    assert '_cache_of_costly_method_1' in s2.__dict__

    # Make sure all keys exist in both caches
    cache_1 = s1.__dict__['_cache_of_costly_method_1']
    cache_2 = s2.__dict__['_cache_of_costly_method_1']
    assert cache_1.is_cached((s1, 10)) is True
    assert cache_1.is_cached((s1, 20)) is True
    assert cache_1.is_cached((s1, 30)) is True
    assert cache_1.is_cached((s1, 1)) is False
    assert cache_1.is_cached((s1, 2)) is False
    assert cache_1.is_cached((s1, 3)) is False
    assert cache_2.is_cached((s2, 1)) is True
    assert cache_2.is_cached((s2, 2)) is True
    assert cache_2.is_cached((s2, 3)) is True
    assert cache_2.is_cached((s2, 10)) is False
    assert cache_2.is_cached((s2, 20)) is False
    assert cache_2.is_cached((s2, 30)) is False


test_1_one_service_two_methods()
test_2_two_services_one_method()