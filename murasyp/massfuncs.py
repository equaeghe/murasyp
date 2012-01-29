from itertools import repeat
from collections import Set
from fractions import Fraction
from murasyp import _make_rational
from murasyp.vectors import Vector
from murasyp.gambles import Gamble

class UMFunc(Vector):
    """(Unit) mass functions map states or events to abstract mass values

    This class derives from :class:`~murasyp.vectors.Vector`, so its methods
    apply here as well.

    What has changed:

    * There is a new constructor. If `data` is a :class:`~collections.Set`,
      then the mass is spread over its elements uniformly.

      >>> UMFunc(set('abc'))
      UMFunc({'a': '1/3', 'c': '1/3', 'b': '1/3'})

    * Its total mass, i.e., the sum of its values, is one and its domain
      coincides with its support.

      >>> UMFunc({'a': -.6, 'b': 1.2, 'c': 1.4, 'd': 0})
      UMFunc({'a': '-3/10', 'c': '7/10', 'b': '3/5'})
      >>> UMFunc({'a': -1, 'b': 1})
      Traceback (most recent call last):
        ...
      ValueError: no UMFunc can be constructed from a Mapping {'a': -1, 'b': 1} with ...

    * Restriction becomes conditioning, i.e., it includes renormalization and
      may be impossible if the conditioning event has zero net mass assigned.

      >>> UMFunc({'a': -.6, 'b': 1.2, 'c': 1.4}) | {'a', 'b', 'd'}
      UMFunc({'a': -1, 'b': 2})
      >>> UMFunc({'a': -1, 'b': 1, 'd': 1}) | {'a', 'c', 'd'}
      Traceback (most recent call last):
        ...
      ValueError: ...

    * Mass functions can be used to to express weighted sums of
      :class:`~murasyp.gambles.Gamble` values using standard product notation
      (think 'expectation' if the mass function is a
      :class:`~murasyp.massfuncs.PMFunc`).

      >>> m = UMFunc({'a': 1.6, 'b': -.6})
      >>> f = Gamble({'a': 13, 'b': -3})
      >>> m * f
      Fraction(113, 5)

      Take note, however, that the domain of the gamble acts as a conditioning event (so one can calculate conditional expectations without explicitly
      calculating conditional mass functions).

      >>> m = UMFunc({'a': '1/3', 'b': '1/6', 'c': '1/2'})
      >>> f = Gamble({'a': 1, 'b': -1, 'c': 0})
      >>> m * f
      Fraction(1, 6)
      >>> m * (f | f.support())
      Fraction(1, 3)
      >>> (m | f.support()) * f
      Fraction(1, 3)

    * Arithmetic with unit mass functions results in a vector, which may be
      converted to a unit mass function in case it satisfies the conditions.

      >>> m = UMFunc({'a': 1.7, 'b': -.7})
      >>> n = UMFunc({'a': .5, 'b': .5})
      >>> m + n
      Vector({'a': '11/5', 'b': '-1/5'})
      >>> UMFunc(.5 * m + n / 2)
      UMFunc({'a': '11/10', 'b': '-1/10'})

    """

    def __init__(self, data):
        """Create a unit mass function"""
        if isinstance(data, Set): # uniform
            data = dict(zip(data, repeat(Fraction(1, len(data)))))
        umfunc = Vector(data).sum_normalized()
        if umfunc == None:
            raise ValueError("no UMFunc can be constructed from a Mapping "
                             + str(data) + " with a total mass of zero")
        Vector.__init__(self, umfunc | umfunc.support())

    def __or__(self, other):
        """Mass function conditional on the given event"""
        return type(self)(Vector(self) | other)

    def __mul__(self, other):
        """'Expectation' of a gamble"""
        if isinstance(other, Gamble):
            pspace = self.domain() & other.domain()
            return sum((self | pspace)[x] * other[x] for x in pspace)
        else:
            return Vector(self) * other

    def __add__(self, other):
        """Pointwise addition of unit mass functions and vectors"""
        if isinstance(other, Vector):
            return Vector(self) + Vector(other)
        else:
            raise TypeError("can only add a vector to a unit mass function, not"
                            + " '" + type(other).__name__ + "'")

    def __div__(self, other):
        """Scalar division of mass assignments"""
        other = _make_rational(other)
        return Vector(self) / other

    __rmul__ = __mul__


class PMFunc(UMFunc):
    """Probability mass functions map states to probability mass

    This class derives from :class:`~murasyp.massfuncs.UMFunc`,
    so its methods apply here as well.

    What has changed:

    * Its values have to be nonnegative.

      >>> PMFunc({'a': -1, 'b': 2})
      Traceback (most recent call last):
      ...
      ValueError: no PMFunc can be constructed from a Mapping {'a': -1, 'b': 2} with ...

    """

    def __init__(self, data):
        """Create a probability mass function"""
        UMFunc.__init__(self, data)
        if not self.is_nonnegative():
            raise ValueError("no PMFunc can be constructed from a Mapping "
                             + str(data) + " with negative values")
