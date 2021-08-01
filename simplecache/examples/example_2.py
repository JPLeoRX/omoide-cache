import time
from simplecache import simplecache, ExpireMode


class ExampleService:
    @simplecache(max_allowed_size=10, size_expire_mode=ExpireMode.ACCESS_COUNT_BASED)
    def time_consuming_method(self, x: int) -> int:
        time.sleep(2.0)
        return x * x
