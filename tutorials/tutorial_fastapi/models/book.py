from pydantic import BaseModel
from simplestr import gen_str_repr


@gen_str_repr
class Book(BaseModel):
    title: str
    author: str
    year_published: int

    def __init__(self, title: str, author: str, year_published: int):
        super().__init__(title=title, author=author, year_published=year_published)
