# Omoide Cache
Caching doesn't need to be hard anymore. With just a few lines of code **Omoide Cache** will instantly bring your Python services to the next level!

# Description
This is a robust, highly tunable and easy-to-integrate in-memory cache solution written in pure Python, with no dependencies.

It is designed to be a method level cache, wrapping around a single class method, using method call arguments as cache key and storing its return value. 

Customizable to suit your specific use-case, provides various expiry and refresh options.

Very user-friendly, super easy to integrate with a simple decorator (i.e. annotation, for those coming from Java), no need to add complicated logic into your code, just use `@omoide_cache()` on top of any method in your services. It will auto-generate a cache for your method with default settings. You can further adjust these settings through decorator parameters.

### When to use?
- You got a heavy call to the data source, where the data is read way more often than it is updated.
- You have CPU intensive computation logic, that takes a few seconds to complete, but can is frequently called with same input parameters.

### When not to use?
- On methods that are not expected to be frequently called with the same arguments (e.g. image processing / OCR / ML models with image inputs)
- On methods that return new values each time they are called, even with the same arguments.
- When you expect argument objects or returned objects to take-up a lot of memory. Cache will quickly eat up your ram if you don't setup expiry modes properly.
- Functions that are declared outside of class is a no go.  

Fair warning - this project is in the earliest stage of its lifecycle, there will be a lot of improvement and bug fixes in the future. All suggestions and bug reports are highly welcome!

# Installation
 
## Normal installation
```bash
pip install omoide-cache
```

## Development installation
```bash
git clone https://github.com/jpleorx/omoide-cache.git
cd omoide-cache
pip install --editable .
```

# Examples
#### 1 - Basic usage example
```python
import time
from omoide_cache import omoide_cache


# A class where cache was added to a simulated long running method
class ExampleService:
    @omoide_cache()
    def time_consuming_method(self, x: int) -> int:
        time.sleep(2.0)
        return x * x


service = ExampleService()

# The first call will execute real logic and store the result in cache
service.time_consuming_method(1)

# The second call will get results from cache
service.time_consuming_method(1)
```

#### 2 - Example with size limit
Here we add a cache that will drop an item least frequently accessed when the cache becomes too large.
```python
import time
from omoide_cache import omoide_cache, ExpireMode


class ExampleService:
    @omoide_cache(max_allowed_size=10, size_expire_mode=ExpireMode.ACCESS_COUNT_BASED)
    def time_consuming_method(self, x: int) -> int:
        time.sleep(2.0)
        return x * x
```

#### 3 - Example with timed expiry
Here the cache will automatically remove items that were last accessed more than 2 minutes ago.
```python
import time
from omoide_cache import omoide_cache


class ExampleService:
    @omoide_cache(expire_by_access_duration_s=120)
    def time_consuming_method(self, x: int) -> int:
        time.sleep(2.0)
        return x * x
```
Alternatively we can remove items that were computed more than 2 minutes ago.
```python
import time
from omoide_cache import omoide_cache


class ExampleService:
    @omoide_cache(expire_by_computed_duration_s=120)
    def time_consuming_method(self, x: int) -> int:
        time.sleep(2.0)
        return x * x
```

#### 4 - Example with async refresh
Here the cache will asynchronously refresh items that were computed more than 2 minutes ago. Attempt to refresh will be performed every 10 seconds.
```python
import time
from omoide_cache import omoide_cache, RefreshMode


class ExampleService:
    @omoide_cache(refresh_duration_s=120, refresh_period_s=10, refresh_mode=RefreshMode.INDEPENDENT)
    def time_consuming_method(self, x: int) -> int:
        time.sleep(2.0)
        return x * x
```

# Known bugs
* You need to use the decorator with parentheses all the time, even when you don't specify any arguments, so use `@omoide_cache()`, but not `@omoide_cache`. I honestly have no fucking idea why there's this weird behaviour in decorators, will do my best to fix it in future updates.

# Links
In case you’d like to check my other work or contact me:
* [Personal website](https://tekleo.net/)
* [GitHub](https://github.com/jpleorx)
* [PyPI](https://pypi.org/user/JPLeoRX/)
* [DockerHub](https://hub.docker.com/u/jpleorx)
* [Articles on Medium](https://medium.com/@leo.ertuna)
* [LinkedIn (feel free to connect)](https://www.linkedin.com/in/leo-ertuna-14b539187/)