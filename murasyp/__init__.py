from collections import Hashable

__version__ = '(git)'
__release__ = __version__

class Freezable(Hashable):
    """Hashable objects that can be made immutable

      :type `frozen`: :class:`~bool`, or `None` to make it permanently frozen

    This class subclasses :class:`~collections.Hashable`; its mutability can be
    controlled using the `frozen` parameter and the
    :meth:`~murasyp.Freezable.freeze` and :meth:`~murasyp.Freezable.thaw`
    methods.

    >>> class X(Freezable):
    ...
    ...     def __init__(self, content, frozen):
    ...         Freezable.__init__(self, frozen)
    ...         self._content = content
    ...
    ...     @Freezable.freeze_safe
    ...     def change(self, content):
    ...         self._content = content
    ...
    >>> x = X('a', False); x._content
    'a'
    >>> x.change('b'); x._content
    'b'
    >>> x.freeze()
    >>> x.change('c'); x._content
    Traceback (most recent call last):
      ...
    TypeError: frozen objects are immutable
    'b'
    >>> x.thaw()
    >>> x.change('c'); x._content
    'c'

    This class should be used when objects that are built up in a number
    of steps, e.g., by subsequently adding aspects, should later be contained as
    keys in :class:`~collections.Set` or :class:`~collections.Mapping`. If a key
    is modified after it became a key, strange things may happen:

    >>> class X(Freezable):
    ...
    ...     def __init__(self, content, frozen):
    ...             Freezable.__init__(self, frozen)
    ...             self._content = content
    ...
    ...     @Freezable.freeze_safe
    ...     def change(self, content):
    ...             self._content = content
    ...
    ...     __hash__ = lambda self: hash(self._content)
    ...
    ...     __eq__ = lambda self, other: hash(self) == hash(other)
    ...
    >>> s = {X(3, False)}
    >>> X(3, True) in s
    True
    >>> for x in s: x.change(4)
    ...
    >>> for x in s: x._content
    ...
    4
    >>> X(3, True) in s
    False
    >>> X(4, True) in s
    False
    >>> X(4, False) in s
    False

    So it is good practice to :meth:`~murasyp.Freezable.freeze` a
    :class:`~murasyp.Freezable` before using it as a key.

    """

    def __init__(self, frozen=True):
        self._frozen = frozen

    __hash__ = lambda self: NotImplementedError

    @classmethod
    def freeze_safe(cls, method):
        """Decorater to make Freezable subclass methods aware of mutability"""
        def freeze_safe_method(self, *args, **kwargs):
            if self._frozen:
                raise TypeError("frozen objects are immutable.")
            else:
                method(self, *args, **kwargs)
        return freeze_safe_method

    def freeze(self):
        """Freeze the object, i.e., make it effectively immutable"""
        self._frozen = True

    def thaw(self):
        """Thaw the object, i.e., make it effectively mutable"""
        if self._frozen == None:
            raise TypeError(repr(self) + " cannot be thawed")
        else:
            self._frozen = False
