import time
from omoide_cache import omoide_cache, RefreshMode


class ExampleService:
    @omoide_cache(refresh_duration_s=120, refresh_period_s=10, refresh_mode=RefreshMode.INDEPENDENT)
    def time_consuming_method(self, x: int) -> int:
        time.sleep(2.0)
        return x * x
