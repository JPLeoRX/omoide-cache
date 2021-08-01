import inspect
from omoide_cache.cache import ExpireMode, RefreshMode, Cache


# This is a very simple decorator version of the cache. It attached itself to the method, and proxies all requests to the method throught the cache
# Performance is yet under question, as we rely heavily on reflections to make this all work
# Basically for each annotated method we create a new cache, and bind it to the method's object instance as a new field
# Then each call to a method is forwarded into the cache

# All cache creation parameters are kept as decorator arguments, so you can tweak the settings easily

# THIS WILL CRASH ON FUNCTIONS THAT ARE NOT CLASS METHODS!!!!

# TODO, for some weird reason this works only with "@cache_decorator(...)" call, while with no arguments "@cache_decorator" fails
#  Needs more time and investigation why that happens. If you want to use it without arguments just add "@cache_decorator()", keep empty parantheses
def omoide_cache(max_allowed_size: int = 100, size_expire_mode: str = ExpireMode.ACCESS_COUNT_BASED,
                 expire_by_computed_duration_s: int = -1, expire_by_access_duration_s: int = -1,
                 refresh_duration_s: int = -1, refresh_mode: str = RefreshMode.COUPLED, refresh_period_s: int = -1,
                 debug: bool = False):
    def cache_decorator_inner(function):
        def wrapper_function(*args, **kwargs):
            # Find name of current method & object to which it is bound
            call_arguments = inspect.getcallargs(function, *args, **kwargs)
            function_name = function.__name__
            function_object = call_arguments['self']

            # Determine name of the cache
            cache_field_name = '_cache_of_' + function_name

            # Create new cache if needed
            if not hasattr(function_object, cache_field_name):
                cache = Cache(
                    function,
                    max_allowed_size=max_allowed_size, size_expire_mode=size_expire_mode,
                    expire_by_computed_duration_s=expire_by_computed_duration_s, expire_by_access_duration_s=expire_by_access_duration_s,
                    refresh_duration_s=refresh_duration_s, refresh_mode=refresh_mode, refresh_period_s=refresh_period_s,
                    debug=debug
                )

                setattr(function_object, cache_field_name, cache)

            # Get cache, and run it, then return the result
            cache = getattr(function_object, cache_field_name)
            result = cache.get(args, kwargs)
            return result
        return wrapper_function
    return cache_decorator_inner
