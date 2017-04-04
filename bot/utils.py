"""Provides various utils."""


class _decorator(object):
    """Adopts decorator function to methods and functions."""

    def __init__(self, decorator, func):
        self.decorator = decorator
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.decorator(self.func)(*args, **kwargs)

    def __get__(self, instance, owner):
        return self.decorator(self.func.__get__(instance, owner))


def decorator(decorator):
    def wrapper(func):
        return _decorator(decorator, func)
    return wrapper
