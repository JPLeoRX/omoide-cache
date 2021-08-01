from omoide_cache.cache_decorator import omoide_cache


class CalculationService:
    @omoide_cache()
    def weird_method(self, x: float, y: float, z: float = 0) -> float:
        return x * y + z


service = CalculationService()

assert service.weird_method(1, 2) == 2.0
assert service.weird_method(2, 1) == 2.0
assert service.weird_method(3, 2) == 6.0
assert service.weird_method(2, 3) == 6.0
assert service.weird_method(1, 1, 7) == 8.0
assert service.weird_method(2, 8, 10) == 26.0
assert service.weird_method(2, 8, z=10) == 26.0
assert service.weird_method(20, 2, z=5) == 45.0
