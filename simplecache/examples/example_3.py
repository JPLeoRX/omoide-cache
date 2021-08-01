import time
from simplecache import simplecache


class ExampleService:
    @simplecache(expire_by_access_duration_s=120)
    def time_consuming_method(self, x: int) -> int:
        time.sleep(2.0)
        return x * x
