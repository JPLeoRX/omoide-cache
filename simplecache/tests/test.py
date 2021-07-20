import time
import threading
import operator
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
    def __init__(self, call_to_execute, max_allowed_size: int = 2, expire_mode: str = 'ACCESS_COUNT_BASED'):
        self.expire_mode_update_time_based = 'UPDATE_TIME_BASED'
        self.expire_mode_access_time_based = 'ACCESS_TIME_BASED'
        self.expire_mode_access_count_based = 'ACCESS_COUNT_BASED'

        self.max_allowed_size = max_allowed_size # If cache becomes larger than that - results will be removed according to expire mode policy
        self.expire_mode = expire_mode # ACCESS_BASED (invalidate items that were not updated or accessed)
        self.expire_duration_ms = 2 * 60 # If the item is older than this - it gets removed
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


    def _assert_max_size(self):
        while len(self.results_map) > self.max_allowed_size:
            with self.results_map_lock and self.last_computed_map_lock and self.last_accessed_map_lock and self.access_counter_map_lock:
                key = self._find_key_to_remove()
                self.results_map.pop(key)
                self.last_computed_map.pop(key)
                self.last_accessed_map.pop(key)
                self.access_counter_map.pop(key)
                print('Cache._assert_max_size(): Dropped ' + str(key))

    def _find_key_to_remove(self) -> str:
        if self.expire_mode == self.expire_mode_access_time_based:
            return self._find_key_first_accessed()
        elif self.expire_mode == self.expire_mode_update_time_based:
            return self._find_key_first_computed()
        elif self.expire_mode == self.expire_mode_access_count_based:
            return self._find_key_least_accessed()
        else:
            raise RuntimeError('Expire mode ' + str(self.expire_mode) + ' is not implemented yet')

    def _find_key_first_accessed(self):
        return min(self.last_accessed_map.items(), key=operator.itemgetter(1))[0]

    def _find_key_first_computed(self):
        return min(self.last_computed_map.items(), key=operator.itemgetter(1))[0]

    def _find_key_least_accessed(self):
        return min(self.access_counter_map.items(), key=operator.itemgetter(1))[0]

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

        # Track size
        self._assert_max_size()

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
c.get(['abc', 1], {})
c.get(['abc', 1], {})
c.get(['abc', 1], {})
c.get(['abc', 2], {})
c.get(['abc', 3], {})
c.get(['abc', 4], {})
c.get(['abc', 1], {})

print(c.last_accessed_map)
print(c.access_counter_map)

