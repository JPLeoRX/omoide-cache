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
    def __init__(self,
                 call_to_execute,
                 max_allowed_size: int = 2, size_expire_mode: str = 'ACCESS_COUNT_BASED',
                 expire_by_computed_duration_ms: int = -1, expire_by_access_duration_ms: int = -1,
                 refresh_duration_ms: int = -1, refresh_mode: str = 'COUPLED', refresh_period_s: int = -1
                 ):
        # Constants
        self.expire_mode_none = 'NONE'
        self.expire_mode_computed_time_based = 'COMPUTED_TIME_BASED'
        self.expire_mode_accessed_time_based = 'ACCESSED_TIME_BASED'
        self.expire_mode_access_count_based = 'ACCESS_COUNT_BASED'
        self.refresh_mode_none = 'NONE'
        self.refresh_mode_independent = 'INDEPENDENT'
        self.refresh_mode_coupled = 'COUPLED'

        # Main method that is used to populate the cache
        self.call_to_execute = call_to_execute

        # If cache becomes larger than that - some results will be removed
        # Elements will be dropped from cache according to this expire mode
        self.max_allowed_size = max_allowed_size
        self.size_expire_mode = size_expire_mode
        if self.max_allowed_size < 1:
            raise RuntimeError("max_allowed_size cannot be less than 1")

        # If cache has some elements that were not computed for a long time - we will drop them
        # Leave at -1 to disable
        self.expire_by_computed_duration_ms = expire_by_computed_duration_ms
        self.expire_by_computed_duration_ns = self.expire_by_computed_duration_ms * 1000000
        self.expire_by_computed_enabled = self.expire_by_computed_duration_ms > 0

        # If cache has some elements that were not accessed for a long time - we will drop them
        # Leave at -1 to disable
        self.expire_by_access_duration_ms = expire_by_access_duration_ms
        self.expire_by_access_duration_ns = self.expire_by_access_duration_ms * 1000000
        self.expire_by_access_enabled = self.expire_by_access_duration_ms > 0

        # Automatically re-compute items in cache after certain period passes since their last update
        self.refresh_duration_ms = refresh_duration_ms
        self.refresh_duration_ns = self.refresh_duration_ms * 1000000
        self.refresh_enabled = self.refresh_duration_ms > 0
        self.refresh_mode = refresh_mode
        self.refresh_period_s = refresh_period_s

        # Map that stores the results {key -> result}
        self.results_map = {}
        self.results_map_lock = threading.Lock()

        # Map that stores arguments {key -> (positional_arguments, keyword_arguments)}
        self.arguments_map = {}
        self.arguments_map_lock = threading.Lock()

        # Map that stores last computed timestamps {key -> timestamp in nano-seconds when this key was last computed}
        self.last_computed_map = {}
        self.last_computed_map_lock = threading.Lock()

        # Map that stores last access timestamps {key -> timestamp in nano-seconds when this key was last accessed}
        self.last_accessed_map = {}
        self.last_accessed_map_lock = threading.Lock()

        # Map that stores access counters {key -> number of times this key was accessed}
        self.access_counter_map = {}
        self.access_counter_map_lock = threading.Lock()

        # Launch periodic refresh
        if self.refresh_enabled:
            if self.refresh_mode == self.refresh_mode_independent:
                self._refresh_periodic()


    def _assert_expire_max_size(self):
        while len(self.results_map) > self.max_allowed_size:
            with self.results_map_lock and self.arguments_map_lock and self.last_computed_map_lock and self.last_accessed_map_lock and self.access_counter_map_lock:
                key = self._find_key_to_remove_for_expire_max_size()
                self.results_map.pop(key)
                self.arguments_map.pop(key)
                self.last_computed_map.pop(key)
                self.last_accessed_map.pop(key)
                self.access_counter_map.pop(key)
                print('Cache._assert_expire_max_size(): Dropped ' + str(key))

    def _assert_expire_by_computed_duration(self):
        # If expire by computed is enabled
        if self.expire_by_computed_enabled:
            with self.last_computed_map_lock:
                # Get next drop candidate
                key = self._find_key_first_computed()

                # Calculate how long ago was this key computed
                last_computed_timestamp_ns = self.last_computed_map[key]
                now_timestamp_ns = time.time_ns()
                delta_ns = now_timestamp_ns - last_computed_timestamp_ns

                # If longer than our expire duration - drop this key
                if delta_ns > self.expire_by_computed_duration_ns:
                    with self.results_map_lock and self.arguments_map_lock and self.last_accessed_map_lock and self.access_counter_map_lock:
                        self.results_map.pop(key)
                        self.arguments_map.pop(key)
                        self.last_computed_map.pop(key)
                        self.last_accessed_map.pop(key)
                        self.access_counter_map.pop(key)
                        print('Cache._assert_expire_by_computed_duration(): Dropped ' + str(key))

    def _assert_expire_by_access_duration(self):
        # If expire by access is enabled
        if self.expire_by_access_enabled:
            with self.last_accessed_map_lock:
                # Get next drop candidate
                key = self._find_key_first_accessed()

                # Calculate how long ago was this key accessed
                last_accessed_timestamp_ns = self.last_accessed_map[key]
                now_timestamp_ns = time.time_ns()
                delta_ns = now_timestamp_ns - last_accessed_timestamp_ns

                # If longer than our expire duration - drop this key
                if delta_ns > self.expire_by_access_duration_ns:
                    with self.results_map_lock and self.arguments_map_lock and self.last_computed_map_lock and self.access_counter_map_lock:
                        self.results_map.pop(key)
                        self.arguments_map.pop(key)
                        self.last_computed_map.pop(key)
                        self.last_accessed_map.pop(key)
                        self.access_counter_map.pop(key)
                        print('Cache._assert_expire_by_access_duration(): Dropped ' + str(key))

    def _find_key_to_remove_for_expire_max_size(self) -> str:
        if self.size_expire_mode == self.expire_mode_accessed_time_based:
            return self._find_key_first_accessed()
        elif self.size_expire_mode == self.expire_mode_computed_time_based:
            return self._find_key_first_computed()
        elif self.size_expire_mode == self.expire_mode_access_count_based:
            return self._find_key_least_accessed()
        else:
            raise RuntimeError('Size expire mode ' + str(self.size_expire_mode) + ' is not implemented yet')

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
        needs_to_be_computed = False
        with self.results_map_lock:
            if key not in self.results_map:
                needs_to_be_computed = True
        if needs_to_be_computed:
            computed_result = self._compute_result(positional_arguments, keyword_arguments)
            self._update_in_result_map(key, computed_result)
            self._update_in_arguments_map(key, positional_arguments, keyword_arguments)
            self._update_in_last_computed_map(key)

        # Get key from the map
        result = self.results_map[key]

        # Update all map data
        self._update_in_last_accessed_map(key)
        self._update_in_access_counter_map(key)

        # Track size
        self._assert_expire_max_size()
        self._assert_expire_by_access_duration()
        self._assert_expire_by_computed_duration()

        # Force refresh
        if self.refresh_enabled:
            if self.refresh_mode == self.refresh_mode_coupled:
                self._refresh_async()

        t2 = time.time()
        print('Cache.get() With positional_arguments=' + str(positional_arguments) + ', keyword_arguments=' + str(keyword_arguments) + ' took ' + str(round(t2 - t1, 2)) + ' seconds')
        return result

    def _refresh(self):
        t1 = time.time()

        # If we can refresh
        if self.refresh_enabled:
            # Copy keys
            keys = []
            with self.results_map_lock:
                for key in self.results_map:
                    keys.append(key)

            # Iterate over keys
            for key in keys:
                # Calculate how long ago was this key computed
                last_computed_timestamp_ns = self.last_computed_map[key]
                now_timestamp_ns = time.time_ns()
                delta_ns = now_timestamp_ns - last_computed_timestamp_ns

                # If longer than our refresh duration - update this key
                if delta_ns > self.refresh_duration_ns:
                    t3 = time.time()
                    positional_arguments, keyword_arguments = self.arguments_map[key]
                    computed_result = self._compute_result(positional_arguments, keyword_arguments)
                    self._update_in_result_map(key, computed_result)
                    self._update_in_last_computed_map(key)
                    t4 = time.time()
                    print('Cache._refresh(): Update of result for positional_arguments=' + str(positional_arguments) + ', keyword_arguments=' + str(keyword_arguments) + ' took ' + str(round(t4 - t3, 2)) + ' seconds')

        # If not - raise error
        else:
            raise RuntimeError('Refresh was called, but refresh is not enabled!')

        t2 = time.time()
        print('Cache._refresh(): Complete refresh took ' + str(round(t2 - t1, 2)) + ' seconds')

    def _refresh_async(self):
        threading.Thread(target=self._refresh, args=[]).start()

    def _refresh_periodic(self):
        self._refresh()
        threading.Timer(self.refresh_period_s, self._refresh_periodic).start()

    def _build_key(self, positional_arguments: List, keyword_arguments: Dict) -> str:
        return 'Key{positional_arguments=' + str(positional_arguments) + '; keyword_arguments=' + str(keyword_arguments) + '}'

    def _compute_result(self, positional_arguments: List, keyword_arguments: Dict):
        return self.call_to_execute(*positional_arguments, **keyword_arguments)

    def _update_in_result_map(self, key: str, result):
        with self.results_map_lock:
            self.results_map[key] = result

    def _update_in_arguments_map(self, key: str, positional_arguments: List, keyword_arguments: Dict):
        with self.arguments_map_lock:
            self.arguments_map[key] = (positional_arguments, keyword_arguments)

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

