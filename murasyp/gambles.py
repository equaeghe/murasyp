from collections import Hashable
from itertools import repeat, izip
from murasyp import RealValFunc
from murasyp.events import Event

class Gamble(RealValFunc, Hashable):
    """An immutable, hashable real-valued function"""

    def __init__(self, data, number_type=None):
        """Create a gamble"""
        if isinstance(data, Event):
            data = dict(izip(data, repeat(1)))
        RealValFunc.__init__(self, data, number_type)

    __repr__ = lambda self: 'Gamble(' + self._mapping.__repr__() + ')'

    def __getitem__(self, x):
        try:
            return self._mapping[x]
        except KeyError:
            return self.make_number(0)

    def pspace(self):
        """The gamble's possibility space"""
        return self.domain()

    def __hash__(self):
        return hash((self.domain,
                     tuple(self._mapping[x] for x in self.pspace())))

    def __add__(self, other):
        """Addition of real-valued functions and scalars"""
        if isinstance(other, self.NumberType):
            return self._scalar(other, '__add__')
        else:
            return RealValFunc.__add__(self, other, '__add__')

    __radd__ = __add__

    def __mul__(self, other):
        """Pointwise multiplication of real-valued functions"""
        if isinstance(other, Gamble):
            return self._pointwise(other, '__mul__')
        else:
            return RealValFunc.__mul__(self, other, '__mul__')

    def __or__(self, other):
        """Restriction or extension with zero

        >>> f = Gamble({'a': 1, 'b': -1})
        >>> A = Event(['b', 'c'])
        >>> f | A
        Gamble({'c': 0.0, 'b': -1.0})

        """
        if isinstance(other, Event):
            return type(self)(dict((x, self[x]) for x in other),
                              self.number_type)
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
                                   for x in self for y in other),
                              self.number_type)
        else:
            raise TypeError("the argument must be an Event")

    _domain_joiner = lambda self, other: self.domain() | other.domain()

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
