import random
import time
from typing import List

from omoide_cache.examples.example_active_users.user import User
from omoide_cache.cache_decorator import omoide_cache
from omoide_cache.cache import RefreshMode


class UserService:
    @omoide_cache(refresh_duration_s=10, refresh_period_s=3, refresh_mode=RefreshMode.INDEPENDENT)
    def get_active_users(self) -> List[User]:
        print('UserService.get_active_users(): Generating list...')
        time.sleep(1)
        result = []
        number_of_users_to_return = random.randint(3, 12)
        for i in range(0, number_of_users_to_return):
            result.append(self.get_random_user())
        return result

    def get_random_user(self) -> User:
        name = self._get_random_name()
        age = self._get_random_age()
        return User(name, age)

    def _get_random_name(self) -> str:
        names = [
            'Paige',
            'Venita',
            'Evangelina',
            'Kecia',
            'Delicia',
            'Lorette',
            'Retha',
            'Lasandra',
            'Leeanne',
            'Claribel',
            'Britta',
            'Carolann',
            'Tracey',
            'Leif',
            'Hiroko',
            'Shelton',
            'Beth',
            'Reed',
            'Samella',
            'Charmaine',
        ]
        random_index = random.randint(0, len(names) - 1)
        return names[random_index]

    def _get_random_age(self) -> int:
        return random.randint(20, 70)
