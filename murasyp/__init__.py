__version__ = '0.1'
__release__ = __version__

from numbers import Real
from fractions import Fraction
from collections import Mapping

def _make_real(value):
    if isinstance(value, Real):
        return value
    elif isinstance(value, str):
        return Fraction(value)
    else:
        raise ValueError(repr(value) + "is not a Real number")

class RealValFunc(Mapping):
    """Immutable real-valued functions

        :param: a mapping (such as a :class:`dict`) to real values,
            i.e., :class:`~numbers.Real`, which includes the built-in types
            :class:`float` and :class:`int`, but also
            :class:`~fractions.Fraction`, which can be used for exact
            arithmetic. The fractions may be given in their
            :class:`str`-representation.
        :type: :class:`~collections.Mapping`

    Members behave like typical real-valued functions: their domain, range,
    support, and individual values are accessible. Morever, they form a vector
    space; i.e., scalar multiplication as well as pointwise addition and
    subtraction is possible.

    >>> f = RealValFunc({'a': 1.1, 'b': '-1/2','c': 0})
    >>> f
    RealValFunc({'a': 1.1, 'c': 0, 'b': Fraction(-1, 2)})
    >>> f['a']
    1.1
    >>> g = RealValFunc({'b': '.6', 'c': -2, 'd': 0.0})
    >>> g
    RealValFunc({'c': -2, 'b': Fraction(3, 5), 'd': 0.0})
    >>> (.3 * f - g) * Fraction(1, 2)
    RealValFunc({'c': 1.0, 'b': -0.375})

    .. note::

      Notice that the domain of results of sums and differences is the
      intersection of the respective domains.

    """

    def __init__(self, mapping, number_type=None):
        """Create a real-valued function"""
        if isinstance(mapping, Mapping):
            self._mapping = dict((element, _make_real(value))
                                 for element, value in mapping.items())
        else:
            raise TypeError("specify a mapping")

    __len__ = lambda self: len(self._mapping)
    __iter__ = lambda self: iter(self._mapping)
    __contains__ = lambda self, element: element in self._mapping
    __getitem__ = lambda self, element: self._mapping[element]
    __repr__ = lambda self: type(self).__name__ + '(' + repr(self._mapping) + ')'
    __str__ = lambda self: str(self._mapping)

    def domain(self):
        """Returns the domain of the real-valued function

        >>> f = RealValFunc({'a': 1, 'b': -1, 'c': 0})
        >>> f.domain()
        frozenset({'a', 'c', 'b'})

        """
        return frozenset(self.keys())

    def range(self):
        """Returns the range of the real-valued function

        >>> f = RealValFunc({'a': 1, 'b': -1, 'c': 0})
        >>> f.range()
        frozenset({0, 1, -1})

        """
        return frozenset(self.values())

    def support(self):
        """Returns the support of the real-valued function

        >>> f = RealValFunc({'a': 1, 'b': -1, 'c': 0})
        >>> f.support()
        frozenset({'a', 'b'})

        """
        return frozenset(element for element, value
                                 in self.items() if value != 0)

    def __add__(self, other):
        """Pointwise addition of real-valued functions"""
        return type(self)(dict((x, self[x] + other[x])
                               for x in self._domain_joiner(other)))

    def _domain_joiner(self, other):
        if type(self) == type(other):
            return iter(self.domain() & other.domain())
        else:
            raise TypeError("cannot combine domains of objects with different"
                            "types: '" + type(self).__name__ + "' and '"
                                       + type(other).__name__ + "'")

    def __mul__(self, other):
        """Scalar multiplication of real-valued functions"""
        other = _make_real(other)
        return type(self)(dict((arg, value * other) for arg, value
                                                    in self.items()))

    __rmul__ = __mul__
    __neg__ = lambda self: self * (-1)
    __sub__ = lambda self, other: self + (-other)
