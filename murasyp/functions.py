from murasyp import _make_rational, Event
from collections import Mapping

class Function(Mapping):
    """Immutable rational-valued functions

      :param: a mapping (such as a :class:`dict`) to Rational values,
          i.e., :class:`~fractions.Fraction`. The fractions
          may be specified by giving an :class:`int`, a :class:`float` or in
          their :class:`str`-representation.
      :type: :class:`~collections.Mapping`

    Members behave like typical rational-valued functions: their domain, range,
    support, and individual values are accessible. Moreover, they form a vector
    space; i.e., scalar multiplication (and division) as well as pointwise
    addition and subtraction is possible.

    >>> f = Function({'a': 1.1, 'b': '-1/2','c': 0})
    >>> f
    Function({'a': Fraction(11, 10), 'c': Fraction(0, 1), 'b': Fraction(-1, 2)})
    >>> f['a']
    Fraction(11, 10)
    >>> g = Function({'b': '.6', 'c': -2, 'd': 0.0})
    >>> (.3 * f - g) / 2
    Function({'c': Fraction(1, 1), 'b': Fraction(-3, 8)})

    .. note::

      Notice that the domain of results of sums and differences is the
      intersection of the respective domains.

    """

    def __init__(self, mapping):
        """Create a rational-valued function"""
        if isinstance(mapping, Mapping):
            self._mapping = dict((element, _make_rational(value))
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
        """Domain of the function

          :returns: the domain of the function, i.e., those values for which the
                    function is defined
          :rtype: :class:`~murasyp.Event`

        >>> Function({'a': 1, 'b': -1, 'c': 0}).domain()
        Event(['a', 'c', 'b'])

        """
        return Event(self.keys())

    def range(self):
        """Range of the function

          :returns: the range of the function, i.e., the set of all values
                    returned by the function
          :rtype: :class:`~murasyp.Event`

        >>> Function({'a': 1, 'b': -1, 'c': 0}).range()
        Event([Fraction(0, 1), Fraction(1, 1), Fraction(-1, 1)])

        """
        return Event(self.values())

    def support(self):
        """Support of the function

          :returns: the support of the function, i.e., that part of the domain
                    for which the function is nonzero
          :rtype: :class:`~murasyp.Event`

        >>> Function({'a': 1, 'b': -1, 'c': 0}).support()
        Event(['a', 'b'])

        """
        return Event(element for element, value in self.items() if value != 0)

    def __add__(self, other):
        """Pointwise addition of rational-valued functions"""
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
        """Scalar multiplication of rational-valued functions"""
        other = _make_rational(other)
        return type(self)(dict((arg, value * other) for arg, value
                                                    in self.items()))

    def __div__(self, other):
        """Scalar division of rational-valued functions"""
        other = _make_rational(other)
        return type(self)(dict((arg, value / other) for arg, value
                                                    in self.items()))

    __rmul__ = __mul__
    __neg__ = lambda self: self * (-1)
    __sub__ = lambda self, other: self + (-other)
