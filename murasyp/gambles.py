from itertools import repeat
from collections import Set
from murasyp import _make_rational
from murasyp.vectors import Vector

class Gamble(Vector):
    """Gambles are immutable, hashable rational-valued functions

      :param: a mapping (such as a :class:`dict`) to Rational values,
          i.e., :class:`~fractions.Fraction`. The fractions
          may be specified by giving an :class:`int`, a :class:`float` or in
          their :class:`str`-representation.
      :type: :class:`~collections.Mapping`

    This class derives from :class:`~murasyp.vectors.Vector`, so its methods
    apply here as well. What has changed:

    * pointwise multiplication and scalar addition & subtraction
      have been added;
    * a gamble's domain can be cylindrically extended to the cartesian product
      of its domain and a specified :class:`~collections.Set`.

    >>> f = Gamble({'a': 1.1, 'b': '-1/2','c': 0})
    >>> g = Gamble({'b': '.6', 'c': -2, 'd': 0.0})
    >>> f * g
    Gamble({'a': 0, 'c': 0, 'b': '-3/10', 'd': 0})
    >>> -3 - f
    Gamble({'a': '-41/10', 'c': -3, 'b': '-5/2'})
    >>> f ^ {'e','f'}
    Gamble({('c', 'f'): 0, ('a', 'f'): '11/10', ('a', 'e'): '11/10', ('b', 'f'): '-1/2', ('b', 'e'): '-1/2', ('c', 'e'): 0})

    """

    def __init__(self, data):
        """Create a gamble"""
        if isinstance(data, Set): # indicators
            data = dict(zip(data, repeat(1)))
        Vector.__init__(self, data)

    def __add__(self, other):
        """Also allow addition of gambles and scalars"""
        if isinstance(other, Gamble):
            return Vector.__add__(self, other)
        else:
            other = _make_rational(other)
            return type(self)({arg: value + other
                               for arg, value in self.iteritems()})

    __radd__ = __add__
    __rsub__ = lambda self, other: -(self - other)

    def __mul__(self, other):
        """Pointwise multiplication of gambles"""
        if isinstance(other, Gamble):
            return type(self)({x: self[x] * other[x]
                               for x in self._domain_joiner(other)})
        else:
            return Vector.__mul__(self, other)

    def __xor__(self, other):
        """Cylindrical extension"""
        if isinstance(other, Set):
            return type(self)({(x, y): self[x] for x in self for y in other})
        else:
            raise TypeError("the argument must be a Set")

    def bounds(self):
        """The minimum and maximum values of the gamble

          :returns: the minimum and maximum values of the gamble
          :rtype: a pair (:class:`tuple`) of :class:`~fractions.Fraction`

        >>> Gamble({'a': 1, 'b': 3, 'c': 4}).bounds()
        (Fraction(1, 1), Fraction(4, 1))

        """
        values = self.range()
        return (min(values), max(values))

    def scaled_shifted(self):
        """Shifted and scaled version of the gamble

          :returns: a scaled and shifted version
                    :math:`(f-\min f)/(\max f-\min f)` of the gamble :math:`f`
          :rtype: :class:`~murasyp.gambles.Gamble`

        >>> Gamble({'a': 1, 'b': 3, 'c': 4}).scaled_shifted()
        Gamble({'a': 0, 'c': 1, 'b': '2/3'})

        .. note::

          The zero gamble is returned in case the gamble is constant.

        """
        minval, maxval = self.bounds()
        shift = minval
        scale = maxval - minval
        return (self - shift) if scale == 0 else (self - shift) / scale

    def norm(self):
        """The max-norm of the gamble

          :returns: the max-norm
                    :math:`\|f\|_\infty=\max_{x\in\mathcal{X}}|f(x)|` of the
                    gamble :math:`f`
          :rtype: :class:`~fractions.Fraction`

        >>> Gamble({'a': 1, 'b': 3, 'c': 4}).norm()
        Fraction(4, 1)

        """
        minval, maxval = self.bounds()
        return max(-minval, maxval)

    def normalized(self):
        """Max-norm normalized version of the gamble

          :returns: a normalized version :math:`f/\|f\|_\infty` of the gamble
                    :math:`f`
          :rtype: :class:`~murasyp.gambles.Gamble`

        >>> Gamble({'a': 1, 'b': 3, 'c': 4}).normalized()
        Gamble({'a': '1/4', 'c': 1, 'b': '3/4'})
        >>> Gamble({'a': 0}).normalized() == None
        True

        .. note::

          ``None`` is returned in case the the gamble's norm is zero.

        """
        norm = self.norm()
        return None if norm == 0 else self / norm
