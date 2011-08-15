from murasyp import _make_rational
from murasyp.gambles import Gamble

class Ray(Gamble):
    """Rays are immutable, hashable rational-valued with max-norm one.

      :param: a mapping (such as a :class:`dict`) to Rational values,
          i.e., :class:`~fractions.Fraction`. The fractions
          may be specified by giving an :class:`int`, a :class:`float` or in
          their :class:`str`-representation.
          Not all values may be zero.
      :type: :class:`~collections.Mapping`

    This class derives from :class:`~murasyp.gambles.Gamble`, so its methods
    apply here as well. What has changed:

    * the max-norm is one;
    * the support becomes the domain.

    >>> Ray(Gamble({'a': 5, 'b': -1, 'c': 0}))
    Ray({'a': 1, 'b': '-1/5'})

    Also, arithmetic with rays results in gambles (which can of course be
    converted to rays).

    >>> r = Ray({'a': 1,'b': -2})
    >>> r / 2
    Gamble({'a': '1/4', 'b': '-1/2'})
    >>> Ray(r * r)
    Ray({'a': '1/4', 'b': 1})

    """

    def __init__(self, data):
        """Create a ray"""
        f = Gamble(data).normalized()
        if f == None:
            raise ValueError("rays cannot be identically zero")
        Gamble.__init__(self, f | f.support())

    def __mul__(self, other):
        """Multiplication of rays (and other types)"""
        self = Gamble(self)
        if isinstance(other, Ray):
            other = Gamble(other)
        return self * other

    def __div__(self, other):
        """Scalar division of rays"""
        other = _make_rational(other)
        return Gamble(self) / other

    __rmul__ = __mul__
