from fractions import Fraction
from collections import Hashable

__version__ = '(git)'
__release__ = __version__

def _make_rational(value):
    """Make a Fraction of acceptable input"""
    try:
        return Fraction(str(value))
    except ValueError(repr(value) + " is not a rational number"):
        raise

class Freezable(Hashable):
    """Hashable objects that can be made immutable

      :type `frozen`: :class:`~bool`, or :class:`~NoneType` to make it
        permanently frozen

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

    """

    def __init__(self, frozen=True):
        self._frozen = frozen

    __hash__ = lambda self: NotImplementedError

    @staticmethod
    def freeze_safe(method):
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
