import time
from typing import List
from simplestr import gen_str_repr_eq
from omoide_cache import omoide_cache
from tekleo_common_utils import UtilsId, UtilsTime, UtilsRandom


utils_id = UtilsId()
utils_time = UtilsTime()
utils_random = UtilsRandom()


@gen_str_repr_eq
class Book:
    title: str
    author: str
    year: int
    country: str

    def __init__(self, title: str, author: str, year: int, country: str):
        self.title = title
        self.author = author
        self.year = year
        self.country = country


def time_now_str() -> str:
    return utils_time.format_timestamp_ms(utils_time.get_timestamp_ms_now(), date_format='%d.%m.%Y %H:%M:%S')


def random_book() -> Book:
    return Book(
        utils_random.get_random_docker_name().replace('_', ' ').title(),
        utils_random.get_random_full_name(),
        utils_random.get_random_year(),
        utils_random.get_random_country()
    )


class BookService:
    @omoide_cache(expire_by_computed_duration_s=5.0)
    def get_popular_books(self) -> List[Book]:
        time.sleep(3.0)
        books = [random_book() for i in range(0, 10)]
        print("BookService.get_popular_books(): Generated at " + time_now_str() + ", first book is " + str(books[0]))
        return books


service = BookService()


# Try 1 - will generate initial results
books = service.get_popular_books()
print("Obtained at " + time_now_str() + ", first book is " + str(books[0]) + '\n')

# Try 2 - will return cached initial results
books = service.get_popular_books()
print("Obtained at " + time_now_str() + ", first book is " + str(books[0]) + '\n')

# Delay
print('Sleeping...\n')
time.sleep(6.0)

# Try 3 - will return cached initial results & mark them as expired
books = service.get_popular_books()
print("Obtained at " + time_now_str() + ", first book is " + str(books[0]) + '\n')

# Try 4 - will generate new results
books = service.get_popular_books()
print("Obtained at " + time_now_str() + ", first book is " + str(books[0]) + '\n')
