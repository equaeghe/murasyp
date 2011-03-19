from collections import Hashable
from itertools import repeat, izip
from murasyp import _make_real, RealValFunc
from murasyp.events import Event

class Gamble(RealValFunc, Hashable):
    """An immutable, hashable real-valued function"""

    def __init__(self, data):
        """Create a gamble"""
        if isinstance(data, Event):
            data = dict(izip(data, repeat(1)))
        RealValFunc.__init__(self, data)

    __getitem__ = lambda self, x: self._mapping[x] if x in self else 0
    __hash__ = lambda self: hash(self._mapping)

    def pspace(self):
        """The gamble's possibility space"""
        return self.domain()

    def __add__(self, other):
        """Also allow addition of real-valued functions and scalars"""
        if isinstance(other, Gamble):
            return RealValFunc.__add__(self, other)
        else:
            other = _make_real(other)
            return type(self)(dict((arg, value + other) for arg, value
                                                        in self.items()))

    __radd__ = __add__

    def __mul__(self, other):
        """Pointwise multiplication of real-valued functions"""
        if isinstance(other, Gamble):
            return type(self)(dict((x, self[x] * other[x])
                                   for x in self._domain_joiner(other)))
        else:
            return RealValFunc.__mul__(self, other)

    def _domain_joiner(self, other):
        if type(self) == type(other):
            return iter(self.domain() | other.domain())
        else:
            raise TypeError("cannot combine domains of objects with different"
                            "types: '" + type(self).__name__ + "' and '"
                                       + type(other).__name__ + "'")

    def __or__(self, other):
        """Restriction or extension with zero

        >>> f = Gamble({'a': 1, 'b': -1})
        >>> A = Event(['b', 'c'])
        >>> f | A
        Gamble({'c': 0.0, 'b': -1.0})

        """
        if isinstance(other, Event):
            return type(self)(dict((x, self[x]) for x in other))
        else:
            raise("the argument must be an Event")

    def __xor__(self, other):
        """Cylindrical extension

        >>> f = Gamble({'a': 1, 'b': -1})
        >>> A = Event(['c', 'd'])
        >>> f ^ A
        Gamble({('b', 'c'): -1.0, ('a', 'd'): 1.0,
        ...     ('a', 'c'): 1.0, ('b', 'd'): -1.0})

        """
        if isinstance(other, Event):
            return type(self)(dict(((x, y), self[x])
                                   for x in self for y in other))
        else:
            raise TypeError("the argument must be an Event")

    def norm(self):
        """The max-norm of the gamble

        :returns: the max-norm of the gamble
        :rtype: :class:`~cdd.NumberTypeable.NumberType`

        """
        return max(map(abs, self.range()))

    def normalized(self):
        """Max-norm normalized version of the gamble"""
        norm = self.norm()
        if norm == 0:
            return (self, norm)
        else:
            return ((1 / norm) * self, norm)

    def scaled_shifted(self):
        """Shifted and scaled version of the gamble"""
        values = self.range()
        shift = min(values)
        scale = max(values) - shift
        if scale == 0:
            return ((self - shift), shift, scale)
        else:
            return ((1 / scale) * (self - shift), shift, scale)
