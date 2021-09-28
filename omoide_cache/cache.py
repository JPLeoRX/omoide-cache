import time
import threading
import traceback
import operator
from typing import List, Dict


class ExpireMode:
    NONE = 'NONE'
    COMPUTED_TIME_BASED = 'COMPUTED_TIME_BASED'
    ACCESSED_TIME_BASED = 'ACCESSED_TIME_BASED'
    ACCESS_COUNT_BASED = 'ACCESS_COUNT_BASED'


class RefreshMode:
    NONE = 'NONE'
    COUPLED = 'COUPLED'                                 # Cache results will be checked and re-computed after each get call in a separate thread
    INDEPENDENT = 'INDEPENDENT'                         # Cache results will be periodically checked and re-computed in a separate thread


class Cache:
    def __init__(self,
                 call_to_execute,
                 max_allowed_size: int = 100, size_expire_mode: str = ExpireMode.ACCESS_COUNT_BASED,
                 expire_by_computed_duration_s: int = -1, expire_by_access_duration_s: int = -1,
                 refresh_duration_s: int = -1, refresh_mode: str = RefreshMode.COUPLED, refresh_period_s: int = -1,
                 debug: bool = False
                 ):
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
        self.expire_by_computed_duration_ms = expire_by_computed_duration_s * 1000
        self.expire_by_computed_duration_ns = self.expire_by_computed_duration_ms * 1000000
        self.expire_by_computed_enabled = self.expire_by_computed_duration_ms > 0

        # If cache has some elements that were not accessed for a long time - we will drop them
        # Leave at -1 to disable
        self.expire_by_access_duration_ms = expire_by_access_duration_s * 1000
        self.expire_by_access_duration_ns = self.expire_by_access_duration_ms * 1000000
        self.expire_by_access_enabled = self.expire_by_access_duration_ms > 0

        # Automatically re-compute items in cache after certain period passes since their last update
        self.refresh_duration_ms = refresh_duration_s * 1000
        self.refresh_duration_ns = self.refresh_duration_ms * 1000000
        self.refresh_enabled = self.refresh_duration_ms > 0
        self.refresh_mode = refresh_mode
        self.refresh_period_s = refresh_period_s

        # Debug flag
        self.debug = debug

        # Terminate flag
        self.terminated = False

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
            if self.refresh_mode == RefreshMode.INDEPENDENT:
                self._refresh_independent()

    # Core methods
    #-------------------------------------------------------------------------------------------------------------------
    def _build_key(self, positional_arguments: List, keyword_arguments: Dict) -> str:
        return 'Key{positional_arguments=' + str(positional_arguments) + '; keyword_arguments=' + str(keyword_arguments) + '}'

    def _compute_result(self, positional_arguments: List, keyword_arguments: Dict):
        return self.call_to_execute(*positional_arguments, **keyword_arguments)
    #-------------------------------------------------------------------------------------------------------------------



    # Map thread safe methods
    #-------------------------------------------------------------------------------------------------------------------
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
    #-------------------------------------------------------------------------------------------------------------------



    # Public access method, main thing exposed to the user
    #-------------------------------------------------------------------------------------------------------------------
    def get(self, positional_arguments: List, keyword_arguments: Dict = {}):
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
        self._assert_expire_max_size(key)
        self._assert_expire_by_access_duration()
        self._assert_expire_by_computed_duration()

        # Force refresh
        if self.refresh_enabled:
            if self.refresh_mode == RefreshMode.COUPLED:
                self._refresh_coupled()

        t2 = time.time()
        if self.debug:
            print('Cache.get() With positional_arguments=' + str(positional_arguments) + ', keyword_arguments=' + str(keyword_arguments) + ' took ' + str(round(t2 - t1, 2)) + ' seconds')
        return result

    # Use this only if refresh independent is selected
    def terminate(self):
        self.terminated = True

    def is_cached(self, positional_arguments: List, keyword_arguments: Dict = {}) -> bool:
        key = self._build_key(positional_arguments, keyword_arguments)
        return key in self.results_map
    #-------------------------------------------------------------------------------------------------------------------



    # Expire methods
    #-------------------------------------------------------------------------------------------------------------------
    def _assert_expire_max_size(self, last_accessed_key: str):
        while len(self.results_map) > self.max_allowed_size:
            with self.results_map_lock and self.arguments_map_lock and self.last_computed_map_lock and self.last_accessed_map_lock and self.access_counter_map_lock:
                key = self._find_key_to_remove_for_expire_max_size(last_accessed_key)
                dropped = False
                number_of_tries = 0
                while not dropped and number_of_tries < 10:
                    # Try to drop the key, if a key error occurs (key is missing in one of the maps) - we need to try another key
                    try:
                        self.results_map.pop(key)
                        self.arguments_map.pop(key)
                        self.last_computed_map.pop(key)
                        self.last_accessed_map.pop(key)
                        self.access_counter_map.pop(key)
                        dropped = True
                    except KeyError as keyError:
                        print('Cache._assert_expire_max_size(): WARNING! Failed to drop key ' + str(key) + ', will retry with new one')
                        print('Cache._assert_expire_max_size(): WARNING! stacktrace:', traceback.format_exc())
                        key = self._find_key_to_remove_for_expire_max_size(last_accessed_key)
                        dropped = False
                        number_of_tries = number_of_tries + 1

                # If we failed each drop - clean the cache completely
                if not dropped and number_of_tries >= 10:
                    print('Cache._assert_expire_max_size(): WARNING! Cache has tried to drop keys for 10 times, yet each try failed. Will clean the cache completely now.')
                    self.results_map = {}
                    self.arguments_map = {}
                    self.last_computed_map = {}
                    self.last_accessed_map = {}
                    self.access_counter_map = {}

                # If drop was successful
                else:
                    if self.debug:
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
                        if self.debug:
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
                        if self.debug:
                            print('Cache._assert_expire_by_access_duration(): Dropped ' + str(key))
    #-------------------------------------------------------------------------------------------------------------------



    # Methods that find keys for expire policies
    #-------------------------------------------------------------------------------------------------------------------
    def _find_key_to_remove_for_expire_max_size(self, last_accessed_key: str) -> str:
        if self.size_expire_mode == ExpireMode.ACCESSED_TIME_BASED:
            return self._find_key_first_accessed()
        elif self.size_expire_mode == ExpireMode.COMPUTED_TIME_BASED:
            return self._find_key_first_computed()
        elif self.size_expire_mode == ExpireMode.ACCESS_COUNT_BASED:
            return self._find_key_least_accessed(last_accessed_key)
        else:
            raise RuntimeError('Size expire mode ' + str(self.size_expire_mode) + ' is not implemented yet')

    def _find_key_first_accessed(self):
        return min(self.last_accessed_map.items(), key=operator.itemgetter(1))[0]

    def _find_key_first_computed(self):
        return min(self.last_computed_map.items(), key=operator.itemgetter(1))[0]

    def _find_key_least_accessed(self, last_accessed_key: str):
        key_value_pairs = [p for p in self.access_counter_map.items() if p[0] != last_accessed_key]
        return min(key_value_pairs, key=operator.itemgetter(1))[0]
    #-------------------------------------------------------------------------------------------------------------------



    # Refresh logic
    #-------------------------------------------------------------------------------------------------------------------
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
                    if self.debug:
                        print('Cache._refresh(): Update of result for positional_arguments=' + str(positional_arguments) + ', keyword_arguments=' + str(keyword_arguments) + ' took ' + str(round(t4 - t3, 2)) + ' seconds')

        # If not - raise error
        else:
            raise RuntimeError('Refresh was called, but refresh is not enabled!')

        t2 = time.time()
        if self.debug:
            print('Cache._refresh(): Complete refresh took ' + str(round(t2 - t1, 2)) + ' seconds')

    def _refresh_coupled(self):
        if self.debug:
            print('Cache._refresh_coupled(): Started')

        if self.refresh_enabled:
            if self.refresh_mode == RefreshMode.COUPLED:
                threading.Thread(target=self._refresh, args=[]).start()
            else:
                raise RuntimeError('Refresh coupled was called, but refresh mode is ' + str(self.refresh_mode))
        else:
            raise RuntimeError('Refresh coupled was called, but refresh is not enabled!')

        if self.debug:
            print('Cache._refresh_coupled(): Ended')

    def _refresh_independent(self):
        if self.terminated:
            print('Cache._refresh_independent(): Won\'t run because cache refreshes were terminated')
            return

        if self.debug:
            print('Cache._refresh_independent(): Started')

        if self.refresh_enabled:
            if self.refresh_mode == RefreshMode.INDEPENDENT:
                if self.refresh_period_s >= 1:
                    self._refresh()
                    threading.Timer(self.refresh_period_s, self._refresh_independent).start()
                else:
                    raise RuntimeError('Refresh independent was called, but refresh period is ' + str(self.refresh_period_s))
            else:
                raise RuntimeError('Refresh independent was called, but refresh mode is ' + str(self.refresh_mode))
        else:
            raise RuntimeError('Refresh independent was called, but refresh is not enabled!')

        if self.debug:
            print('Cache._refresh_independent(): Ended')
    #-------------------------------------------------------------------------------------------------------------------
