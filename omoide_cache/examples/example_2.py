import time
from omoide_cache import omoide_cache, ExpireMode


class ExampleService:
    @omoide_cache(max_allowed_size=10, size_expire_mode=ExpireMode.ACCESS_COUNT_BASED)
    def time_consuming_method(self, x: int) -> int:
        time.sleep(2.0)
        return x * x
