import functools


def cached_property_OLD(fn):
    """Decorator to cache compiled object result"""

    # Need to use a mutable type to store...
    cached_value = {}

    @functools.wraps(fn)
    def wrapped(self):
        if 0 not in cached_value:
            cached_value[0] = fn(self)
        return cached_value[0]

    return property(wrapped)


class cached_property(object):
    """ A property that is only computed once per instance and then replaces
        itself with an ordinary attribute. Deleting the attribute resets the
        property.

        Source: https://github.com/bottlepy/bottle/commit/fa7733e0
        """

    def __init__(self, func):
        self.__doc__ = getattr(func, "__doc__")
        self.func = func

    def __get__(self, obj, cls):
        # type: (Any, type) -> Any
        if obj is None:
            return self
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value
