from itertools import repeat
from murasyp import _make_rational
from murasyp.vectors import Vector
from murasyp.events import Event

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
      of its domain and a specified :class:`~murasyp.events.Event`.

    >>> f = Gamble({'a': 1.1, 'b': '-1/2','c': 0})
    >>> g = Gamble({'b': '.6', 'c': -2, 'd': 0.0})
    >>> f * g
    Gamble({'a': Fraction(0, 1), 'c': Fraction(0, 1), 'b': Fraction(-3, 10), 'd': Fraction(0, 1)})
    >>> -3 - f
    Gamble({'a': Fraction(-41, 10), 'c': Fraction(-3, 1), 'b': Fraction(-5, 2)})
    >>> f ^ Event({'e', 'f'})
    Gamble({('c', 'f'): Fraction(0, 1), ('a', 'f'): Fraction(11, 10), ('a', 'e'): Fraction(11, 10), ('b', 'f'): Fraction(-1, 2), ('b', 'e'): Fraction(-1, 2), ('c', 'e'): Fraction(0, 1)})

    """

    def __init__(self, data):
        """Create a gamble"""
        if isinstance(data, Event):
            data = dict(zip(data, repeat(1)))
        Vector.__init__(self, data)

    def __add__(self, other):
        """Also allow addition of gambles and scalars"""
        if isinstance(other, Gamble):
            return Vector.__add__(self, other)
        else:
            other = _make_rational(other)
            return type(self)(dict((arg, value + other) for arg, value
                                                        in self.items()))

    __radd__ = __add__
    __rsub__ = lambda self, other: -(self - other)

    def __mul__(self, other):
        """Pointwise multiplication of gambles"""
        if isinstance(other, Gamble):
            return type(self)(dict((x, self[x] * other[x])
                                   for x in self._domain_joiner(other)))
        else:
            return Vector.__mul__(self, other)

    def __xor__(self, other):
        """Cylindrical extension"""
        if isinstance(other, Event):
            return type(self)(dict(((x, y), self[x])
                                   for x in self for y in other))
        else:
            raise TypeError("the argument must be an Event")

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
        Gamble({'a': Fraction(0, 1), 'c': Fraction(1, 1), 'b': Fraction(2, 3)})

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

        >>> h = Gamble({'a': 1, 'b': 3, 'c': 4})
        >>> h.norm()
        Fraction(4, 1)

        """
        minval, maxval = self.bounds()
        return max(-minval, maxval)

    def normalized(self):
        """Max-norm normalized version of the gamble

          :returns: a normalized version :math:`f/\|f\|_\infty` of the gamble
                    :math:`f`
          :rtype: :class:`~murasyp.gambles.Gamble`

        >>> h = Gamble({'a': 1, 'b': 3, 'c': 4})
        >>> h.normalized()
        Gamble({'a': Fraction(1, 4), 'c': Fraction(1, 1), 'b': Fraction(3, 4)})

        .. note::

          The gamble itself is returned in case it is identically zero.

        """
        norm = self.norm()
        return self if norm == 0 else self / norm
