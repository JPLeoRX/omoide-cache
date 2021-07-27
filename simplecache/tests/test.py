import time
import functools
import inspect
from simplecache.cache import Cache
import threading
import operator
from typing import List, Dict

def get_class_that_defined_method(meth):
    if isinstance(meth, functools.partial):
        return get_class_that_defined_method(meth.func)
    if inspect.ismethod(meth) or (inspect.isbuiltin(meth) and getattr(meth, '__self__', None) is not None and getattr(meth.__self__, '__class__', None)):
        for cls in inspect.getmro(meth.__self__.__class__):
            if meth.__name__ in cls.__dict__:
                return cls
        meth = getattr(meth, '__func__', meth)  # fallback to __qualname__ parsing
    if inspect.isfunction(meth):
        cls = getattr(inspect.getmodule(meth),
                      meth.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0],
                      None)
        if isinstance(cls, type):
            return cls
    return getattr(meth, '__objclass__', None)  # handle special descriptor objects

#
# def cache_decorator(function):
#     def wrapper_function(*args, **kwargs):
#         print(function.__self__)
#         cls = get_class_that_defined_method(function)
#         method_name = function.__name__
#         cache_field_name = 'cache_of_' + method_name
#         cache_object = Cache(function)
#
#         setattr()
#
#
#         # Do something before the function.
#         function(*args, **kwargs)
#         # Do something after the function.
#     return wrapper_function

# class CacheDecorator:
#     def __init__(self, function):
#         self.function = function
#         #print(members)
#         #print(self.__dict__)
#
#     def __call__(self, *args, **kwargs):
#         # Do something before the function.
#         result = self.function(*args, **kwargs)
#         # Do something after the function.
#         return result
#
#
#         # def wrapper_function(*args, **kwargs):
#         #     #print(function.__self__)
#         #     #cls = get_class_that_defined_method(function)
#         #     #method_name = function.__name__
#         #     #cache_field_name = 'cache_of_' + method_name
#         #     #cache_object = Cache(function)
#         #     #setattr()
#         #
#         #     # # Do something before the function.
#         #     # self.function(*args, **kwargs)
#         #     # # Do something after the function.
#         # return wrapper_function





    # def costly_method_cached(self, text: str, number: int) -> float:
    #     return self.cache.get([text, number], {})




s = ExampleService()
print('Get for 1:', s.costly_method(1))
print('Get for 2:', s.costly_method(2))
print('Get for 3:', s.costly_method(3))
print('Get for 1:', s.costly_method(1))
print('Get for 1:', s.costly_method(1))
print('Get for 1:', s.costly_method(1))
print(s.__dict__)

#print(s.__dict__)
# s.costly_method_cached('abc', 2)
# s.costly_method_cached('abc', 3)
# s.costly_method_cached('abc', 1)
# s.costly_method_cached('abc', 2)
# s.costly_method_cached('abc', 4)




# c = Cache(s.costly_method)
# c.get(['abc', 1], {})
# c.get(['abc', 1], {})
# c.get(['abc', 1], {})
# c.get(['abc', 2], {})
# c.get(['abc', 3], {})
# c.get(['abc', 4], {})
# c.get(['abc', 1], {})
#
# print(c.last_accessed_map)
# print(c.access_counter_map)
#
