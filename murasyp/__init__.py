__version__ = '0.1'
__release__ = __version__

from cdd import NumberTypeable, get_number_type_from_sequences
from collections import Mapping

class RealValFunc(Mapping, NumberTypeable):
    """Immutable real-valued functions

    Members are created by passing a mapping (such as a `'dict'`) to real values
    to the constructor.

    They behave like typical real-valued functions: their domain, range,
    support, and individual values are accessible. Morever, they form a vector
    space; i.e., scalar multiplication as well as pointwise addition and
    subtraction is possible.

    >>> f = RealValFunc({'a': 1, 'b': -1, 'c': 0})
    >>> g = RealValFunc({'b': 2, 'c': -2, 'd': 0})
    >>> f['a']
    1.0
    >>> (2 * f - g) * .5
    RealValFunc({'c': 1.0, 'b': -2.0})

    .. note::

      Notice that the domain of results of sums and differences is the intersection of
      the respective domains.

    Furthermore, the type of real values used, `'float'` or `'fraction'` can be
    specified or automatically detected:

    >>> RealValFunc({'b': 2, 'c': -2, 'd': 0}, number_type='fraction')
    RealValFunc({'c': Fraction(-2, 1), 'b': Fraction(2, 1), 'd': Fraction(0, 1)})
    >>> RealValFunc({'b': '1/2', 'c': '-1/2', 'd': '0'}, number_type='float')
    RealValFunc({'c': -0.5, 'b': 0.5, 'd': 0.0})
    >>> h = RealValFunc({'b': '1/2', 'c': '-1/2', 'd': '0'})
    >>> h
    RealValFunc({'c': Fraction(-1, 2), 'b': Fraction(1, 2), 'd': Fraction(0, 1)})
    >>> h * .5
    RealValFunc({'c': Fraction(-1, 4), 'b': Fraction(1, 4), 'd': Fraction(0, 1)})
    >>> from fractions import Fraction
    >>> h * Fraction(1, 4)
    RealValFunc({'c': Fraction(-1, 8), 'b': Fraction(1, 8), 'd': Fraction(0, 1)})

    """

    def __init__(self, mapping, number_type=None):
        """Create a real-valued function

        :param mapping: a mapping to real values.
        :type data: |collections.Mapping|
        :param number_type: The type to use for numbers:
            ``'float'`` or ``'fraction'``. If omitted,
            then :func:`~cdd.get_number_type_from_sequences`
            is used to determine the number type.
        :type number_type: :class:`str`
        """
        if isinstance(mapping, Mapping):
            if number_type is None:
                NumberTypeable.__init__(self,
                    get_number_type_from_sequences(mapping.itervalues()))
            else:
                NumberTypeable.__init__(self, number_type)
            self._mapping = dict((element, self.make_number(value))
                                 for element, value in mapping.iteritems())
        else:
            raise TypeError('specify a mapping')

    __len__ = lambda self: len(self._mapping)
    __iter__ = lambda self: iter(self._mapping)
    __contains__ = lambda self, element: element in self._mapping
    __getitem__ = lambda self, element: self._mapping[element]
    __repr__ = lambda self: type(self).__name__ + '(' + `self._mapping` + ')'
    __str__ = lambda self: str(self._mapping)

    def domain(self):
        """Returns the domain of the real-valued function

        >>> f = RealValFunc({'a': 1, 'b': -1, 'c': 0})
        >>> f.domain()
        frozenset(['a', 'c', 'b'])

        """
        return frozenset(self.keys())

    def range(self):
        """Returns the range of the real-valued function

        >>> f = RealValFunc({'a': 1, 'b': -1, 'c': 0})
        >>> f.range()
        frozenset([0.0, 1.0, -1.0])

        """
        return frozenset(self.values())

    def support(self):
        """Returns the support of the real-valued function

        >>> f = RealValFunc({'a': 1, 'b': -1, 'c': 0})
        >>> f.support()
        frozenset(['a', 'b'])

        """
        return frozenset(element for element, value
                                 in self.iteritems() if value != 0)

    __add__ = lambda self, other: self._pointwise(other, self.NumberType.__add__)
    __mul__ = lambda self, other: self._scalar(other, self.NumberType.__mul__)
    __rmul__ = __mul__
    __neg__ = lambda self: self * (-1)
    __sub__ = lambda self, other: self + (-other)

    def _pointwise(self, other, oper):
        if type(self) != type(other):
            raise TypeError("unsupported operand type(s) for "
                            + oper.__name__ + ": '" + type(self).__name__
                            + "' and '" + type(other).__name__ + "'")
        if self.number_type != other.number_type:
            raise ValueError("number type mismatch")
        return type(self)(dict((arg, oper(self[arg], other[arg]))
                               for arg in self._domain_joiner(other)),
                          number_type=self.number_type)

    _domain_joiner = lambda self, other: iter(self.domain() & other.domain())

    def _scalar(self, other, oper):
        other = self.make_number(other)
        return type(self)(dict((arg, oper(value, other))
                               for arg, value in self.iteritems()),
                          number_type=self.number_type)
