import time

from simplecache.cache_decorator import simplecache

class ExampleService:
    def __init__(self):
        self.power = 3

    @simplecache(debug=True)
    def costly_method(self, number: int) -> float:
        t1 = time.time()
        time.sleep(0.2)
        result = number ** self.power
        t2 = time.time()
        print('ExampleService.costly_method() Took ' + str(round(t2 - t1, 2)) + ' seconds')
        return result


s = ExampleService()
s.costly_method(1)
s.costly_method(1)
s.costly_method(1)
s.costly_method(2)
s.costly_method(1)
s.costly_method(1)
s.costly_method(3)