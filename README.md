# simplecache
Caching doesn't need to be hard anymore. With just a few lines of code **simplecache** will instantly bring your Python services to the next level!

# Description
This is a robust, highly tunable and easy-to-integrate in-memory cache solution written in pure Python, with no dependencies.

It was designed to be a cache around a single method, storing its return value and using method call arguments as cache key.

Very user-friendly, super easy to use with a simple annotation, no need to add complicated integration logic into your code. Simply add `@simplecache()` on top of any method in your services! It will auto-generate a cache for your method with default settings. You can further adjust these settings through annotation parameters. It mirrors normal cache initialization completely.

### When to use? This cache perfectly suits following conditions:
- You got a heavy call to the database, that needs to be.
- You have CPU intensive computation logic, that takes a few seconds to complete, but can be frequently called with same parameters?

### When not to use?
- Do not use on methods that are not expected to be frequently called with the same arguments - image processing / OCR / ML models with image inputs
- Do not use on methods that return new values each time they are called, even with the same arguments.
- Do not use when you expect argument objects or returned objects to take-up a lot of memory. Cache will quickly eat up your ram if you don't setup expiry modes properly. 


This package provides only two annotations:
- `@gen_str` to generate `__str__(self)` method
- `@gen_repr` to generate `__repr__(self)` method
- `@gen_eq` to generate `__eq__(self, other)` method 
- `@gen_str_repr` to generate both `__str__(self)` and `__repr__(self)` methods
- `@gen_str_repr_eq` to generate both `__str__(self)`, `__repr__(self)` and `__eq__(self, other)` methods

# Installation
 
## Normal installation

```bash
pip install simplestr
```

## Development installation

```bash
git clone https://github.com/jpleorx/simplestr.git
cd simplestr
pip install --editable .
```

# Example A (with separate annotations)
```python
from simplestr import gen_str, gen_repr, gen_eq

@gen_str
@gen_repr
@gen_eq
class Rect:
    def __init__(self, x: int, y: int, w: int, h: int):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

rect1 = Rect(1, 2, 3, 4)
rect2 = Rect(10, 20, 30, 40)
print(rect1)
print(rect2)
print([rect1, rect2])
print(rect1 == rect2)
print(rect1 == Rect(1, 2, 3, 4))
```

```
Rect{x=1, y=2, w=3, h=4}
Rect{x=10, y=20, w=30, h=40}
[Rect{x=1, y=2, w=3, h=4}, Rect{x=10, y=20, w=30, h=40}]
False
True
```

# Example B (with joined annotation)
```python
from simplestr import gen_str_repr_eq

@gen_str_repr_eq
class Rect:
    def __init__(self, x: int, y: int, w: int, h: int):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

rect1 = Rect(1, 2, 3, 4)
rect2 = Rect(10, 20, 30, 40)
print(rect1)
print(rect2)
print([rect1, rect2])
print(rect1 == rect2)
print(rect1 == Rect(1, 2, 3, 4))
```

```
Rect{x=1, y=2, w=3, h=4}
Rect{x=10, y=20, w=30, h=40}
[Rect{x=1, y=2, w=3, h=4}, Rect{x=10, y=20, w=30, h=40}]
False
True
```