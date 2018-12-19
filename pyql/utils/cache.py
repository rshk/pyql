import functools


def cached_property(fn):
    """Decorator to cache compiled object result"""

    # Need to use a mutable type to store...
    cached_value = {}

    @functools.wraps(fn)
    def wrapped(self):
        if 0 not in cached_value:
            cached_value[0] = fn(self)
        return cached_value[0]

    return property(wrapped)
