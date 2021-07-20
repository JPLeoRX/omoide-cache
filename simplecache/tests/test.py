import time
import threading
from typing import List, Dict


class ExampleService:
    def costly_method(self, text: str, number: int) -> float:
        t1 = time.time()
        time.sleep(1.0)
        result = len(text) * number
        t2 = time.time()
        print('ExampleService.costly_method() Took ' + str(round(t2 - t1, 2)) + ' seconds')
        return result

class Cache:
    def __init__(self, call_to_execute):
        self.call_to_execute = call_to_execute

        # Map that stores the results {key -> result}
        self.results_map = {}
        self.results_map_lock = threading.Lock()

        # Map that stores last computed timestamps {key -> timestamp in nano-seconds when this key was last computed}
        self.last_computed_map = {}
        self.last_computed_map_lock = threading.Lock()

        # Map that stores last access timestamps {key -> timestamp in nano-seconds when this key was last accessed}
        self.last_accessed_map = {}
        self.last_accessed_map_lock = threading.Lock()

        # Map that stores access counters {key -> number of times this key was accessed}
        self.access_counter_map = {}
        self.access_counter_map_lock = threading.Lock()


    def get(self, positional_arguments: List, keyword_arguments: Dict):
        t1 = time.time()

        # Build key
        key = self._build_key(positional_arguments, keyword_arguments)

        # If the key is not currently stored
        if key not in self.results_map:
            computed_result = self._compute_result(positional_arguments, keyword_arguments)
            self._update_in_result_map(key, computed_result)
            self._update_in_last_computed_map(key)

        # Get key from the map
        result = self.results_map[key]

        # Update all map data
        self._update_in_last_accessed_map(key)
        self._update_in_access_counter_map(key)

        t2 = time.time()
        print('Cache.get() With positional_arguments=' + str(positional_arguments) + ', keyword_arguments=' + str(keyword_arguments) + ' took ' + str(round(t2 - t1, 2)) + ' seconds')
        return result

    def _build_key(self, positional_arguments: List, keyword_arguments: Dict) -> str:
        return 'Key{positional_arguments=' + str(positional_arguments) + '; keyword_arguments=' + str(keyword_arguments) + '}'

    def _compute_result(self, positional_arguments: List, keyword_arguments: Dict):
        return self.call_to_execute(*positional_arguments, **keyword_arguments)

    def _update_in_result_map(self, key: str, result):
        with self.results_map_lock:
            self.results_map[key] = result

    def _update_in_last_computed_map(self, key):
        with self.last_computed_map_lock:
            self.last_computed_map[key] = time.time_ns()

    def _update_in_last_accessed_map(self, key):
        with self.last_accessed_map_lock:
            self.last_accessed_map[key] = time.time_ns()

    def _update_in_access_counter_map(self, key):
        with self.access_counter_map_lock:
            old_value = self.access_counter_map.get(key, 0)
            new_value = old_value + 1
            self.access_counter_map[key] = new_value



s = ExampleService()
c = Cache(s.costly_method)
c.get(['abc', 4], {})
c.get(['abc', 4], {})
c.get(['abc', 5], {})
c.get(['abc', 4], {})
c.get(['abc', 5], {})

print(c.last_accessed_map)
print(c.access_counter_map)

