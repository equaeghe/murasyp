from __future__ import division
from collections import Mapping
from fractions import Fraction

class Function(Mapping):
    """Rational-valued functions

      :type `mapping`: :class:`~collections.Mapping` (such as a :class:`dict`)
        to a representation of :class:`~numbers.Real`

    Features:

    * Values may be specified as :class:`int`, :class:`float`, or
      :class:`~fractions.Fraction`, whose :class:`str`-representation is then
      especially convenient.

      >>> f = Function({'a': 11e-1, 'b': '-1/2','c': 0})
      >>> assert f == Function({'a': '11/10', 'c': 0, 'b': '-1/2'})
      >>> f['a']
      Fraction(11, 10)

      .. note::

        No floats are ever really used; they are immediately converted to
        fractions and should be seen as just a convenient input representation
        for decimal numbers.

    * Scalar multiplication and division, as well as pointwise multiplication,
      addition, and subtraction (also with scalars) is possible.

      >>> f = Function({'a': 1.1, 'b': '-1/2','c': 0})
      >>> g = Function({'b': '.6', 'c': -2, 'd': 0.0})
      >>> assert -1 + (.3 * f - g) / 2 == Function({'c': 0, 'b': '-11/8'})
      >>> assert f * g == Function({'c': 0, 'b': '-3/10'})

      .. note::

        The domain of results of sums and differences is the intersection of
        the respective domains.

    """

    def __init__(self, mapping={}):
        """Create a rational-valued function"""
        if isinstance(mapping, Mapping):
            self._mapping = {arg: self._make_rational(value)
                             for arg, value in mapping.items()}
        else:
            raise TypeError("specify a mapping")

    def _make_rational(self, value):
        """Make a Fraction of acceptable input"""
        if type(value) == float:
            value = str(value) # treat floats as decimal numbers
        try:
            return Fraction(value)
        except ValueError:
            print(repr(value) + " is not a Rational number")

    __len__ = lambda self: len(self._mapping)
    __iter__ = lambda self: iter(self._mapping)
    __contains__ = lambda self, element: element in self._mapping
    __getitem__ = lambda self, element: self._mapping[element]

    def __repr__(self):
        """Return a readable unambiguous string representation"""
        return type(self).__name__ + '(' + str(self) + ')'

    def __str__(self):
        """Return a readable string representation"""
        return ('{' +
                ', '.join(repr(arg) + ': ' +
                          (repr(str(val)) if '/' in str(val) else str(val))
                          for arg, val in self._mapping.items()) +
                '}')

    def domain(self):
        """Domain of the function

          :returns: the domain of the function, i.e., those values for which the
                    function is defined
          :rtype: :class:`frozenset`

        >>> assert (
        ...     Function({'a': 1, 'b': -1, 'c': 0}).domain() ==
        ...     frozenset({'a', 'c', 'b'})
        ... )

        """
        return frozenset(self.keys())

    def range(self):
        """Range of the function

          :returns: the range of the function, i.e., the set of all values
                    returned by the function
          :rtype: :class:`frozenset`

        >>> assert (
        ...     Function({'a': 1, 'b': -1, 'c': 0}).range() ==
        ...     frozenset({Fraction(0, 1), Fraction(1, 1), Fraction(-1, 1)})
        ... )

        """
        return frozenset(self.values())

    def support(self):
        """Support of the function

          :returns: the support of the function, i.e., that part of the domain
                    for which the function is nonzero
          :rtype: :class:`frozenset`

        >>> assert (
        ...     Function({'a': 1, 'b': -1, 'c': 0}).support() ==
        ...     frozenset({'a', 'b'})
        ... )

        """
        return frozenset(arg for arg, value in self.items() if value != 0)

    def _with_scalar(self, other, operator):
        """Application of a binary operator to a function/scalar-pair"""
        try:
            other = self._make_rational(other)
            return type(self)({arg: operator(value, other)
                              for arg, value in self.items()})
        except:
            return NotImplemented

    def _with_function(self, other, operator):
        """pointwise application of a binary operator to a pair of functions"""
        if isinstance(other, type(self)):
            return type(self)({arg: operator(self[arg], other[arg])
                              for arg in self._domain_joiner(other)})
        else:
            raise TypeError("cannot apply '" + operator.__name__ + "'"
                            " to objects of types: '" +
                            type(self).__name__ + "' and '" +
                            type(other).__name__ + "'")

    _domain_joiner = lambda self, other: iter(self.domain() & other.domain())

    def _pointwise(self, other, operator):
        """Pointwise application of a binary operator"""
        try:
            return self._with_function(other, operator)
        except:
            return self._with_scalar(other, operator)

    __add__ = lambda self, other: self._pointwise(other, Fraction.__add__)
    __radd__ = __add__

    __mul__ = lambda self, other: self._pointwise(other, Fraction.__mul__)
    __rmul__ = __mul__

    __truediv__ = lambda self, other: self._with_scalar(other, Fraction.__truediv__)

    __neg__ = lambda self: self * (-1)

    __sub__ = lambda self, other: self + (-other)
    __rsub__ = lambda self, other: -(self - other)
