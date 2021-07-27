from simplestr import gen_str_repr_eq

@gen_str_repr_eq
class User:
    name: str
    age: int

    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age
