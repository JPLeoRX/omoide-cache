import time
from simplecache import simplecache


# A class where cache was added to a simulated long running method
class ExampleService:
    @simplecache()
    def time_consuming_method(self, x: int) -> int:
        time.sleep(2.0)
        return x * x


service = ExampleService()

# The first call will execute real logic and store the result in cache
service.time_consuming_method(1)

# The second call will get results from cache
service.time_consuming_method(1)