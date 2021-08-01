import time
from omoide_cache import omoide_cache


class ExampleService:
    @omoide_cache(expire_by_access_duration_s=120)
    def time_consuming_method(self, x: int) -> int:
        time.sleep(2.0)
        return x * x
