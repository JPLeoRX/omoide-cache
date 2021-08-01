import time
from simplecache import simplecache, RefreshMode


class ExampleService:
    @simplecache(refresh_duration_s=120, refresh_period_s=10, refresh_mode=RefreshMode.INDEPENDENT)
    def time_consuming_method(self, x: int) -> int:
        time.sleep(2.0)
        return x * x
