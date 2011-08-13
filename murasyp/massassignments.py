from itertools import repeat
from collections import Set
from murasyp import _make_rational
from murasyp.vectors import Vector
from murasyp.gambles import Gamble

class MassAssignment(Vector):
    """(Unit) mass assignments are immutable, hashable rational-valued
    functions with values that sum to one.

      :param: a mapping (such as a :class:`dict`) to Rational values,
          i.e., :class:`~fractions.Fraction`. The fractions
          may be specified by giving an :class:`int`, a :class:`float` or in
          their :class:`str`-representation.
          The sum of the values must be nonzero.
      :type: :class:`~collections.Mapping`

    This class derives from :class:`~murasyp.vectors.Vector`, so its methods
    apply here as well. What has changed:

    * its total mass, i.e., sum of values, has to be nonzero;
    * restriction becomes conditioning, i.e., it includes renormalization and
      may be impossible if the conditioning event has zero net mass assigned;
    * the support becomes the domain.

    >>> m = MassAssignment({'a': -.3, 'b': .6, 'c': .7, 'd': 0})
    >>> m
    MassAssignment({'a': Fraction(-3, 10), 'c': Fraction(7, 10), 'b': Fraction(3, 5)})
    >>> m | {'a','b','d'}
    MassAssignment({'a': Fraction(-1, 1), 'b': Fraction(2, 1)})

    Furthermore, mass assignments can be used to to express weighted sums
    of vector values using standard product notation.

    >>> m = MassAssignment({'a': 1.6, 'b': -.6})
    >>> f = Gamble({'a': 13, 'b': -3})
    >>> m * f
    Fraction(113, 5)

    Also, arithmetic with mass assignment results in vectors, which may be
    converted to a mass assignment in case it satisfies the conditions.

    >>> m = MassAssignment({'a': 1.7, 'b': -.7})
    >>> n = MassAssignment({'a': .5, 'b': .5})
    >>> m + n
    Vector({'a': Fraction(11, 5), 'b': Fraction(-1, 5)})
    >>> MassAssignment(.5 * m + n / 2)
    MassAssignment({'a': Fraction(11, 10), 'b': Fraction(-1, 10)})

    """

    def __init__(self, data):
        """Create a mass assignment"""
        if isinstance(data, Set): # uniform distribution
            data = dict(zip(data, repeat(1 / len(data))))
        m = Vector(data)
        if m.mass() != 1:
            raise ValueError("mass assignment must have a total mass of 1")
        Vector.__init__(self, m | m.support())

    def __or__(self, other):
        """Mass function conditional on the given event"""
        return type(self)((Vector(self) | other).sum_normalized())

    def __mul__(self, other):
        """'Expectation' of a gamble"""
        if isinstance(other, Gamble):
            return sum(self[x] * other[x] for x in self)
        else:
            return Vector(self) * other

    def is_pmf(self):
        """Checks whether the mass assignment is a probability mass function

        >>> MassAssignment({'a': 1.6, 'b': -.6}).is_pmf()
        False
        >>> MassAssignment({'a': .4, 'b': .6}).is_pmf()
        True

        """
        return all(val >= 0 for val in self._mapping.itervalues())

    def __add__(self, other):
        """Pointwise addition of mass assignments and vectors"""
        if isinstance(other, Vector):
            return Vector(self) + Vector(other)
        else:
            raise TypeError("can only add a vector to a mass assignment, not '"
                             + type(other).__name__ + "'")

    def __div__(self, other):
        """Scalar division of mass assignments"""
        other = _make_rational(other)
        return Vector(self) / other

    __rmul__ = __mul__
