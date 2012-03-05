from itertools import repeat
from collections import Set
from murasyp import _make_rational
from murasyp.vectors import Vector

class Gamble(Vector):
    """Gambles map states to utility payoffs

    This class derives from :class:`~murasyp.vectors.Vector`, so its methods
    apply here as well.

    What has changed:

    * There is a new constructor. If `data` is a :class:`~collections.Set`,
      then its so-called indicator function is generated.

      >>> Gamble(set('abc'))
      Gamble({'a': 1, 'c': 1, 'b': 1})

    * Pointwise multiplication and scalar addition & subtraction
      have been added.

      >>> f = Gamble({'a': 1.1, 'b': '-1/2', 'c': 0})
      >>> g = Gamble({'b': '.6', 'c': -2, 'd': 0.0})
      >>> f * g
      Gamble({'a': 0, 'c': 0, 'b': '-3/10', 'd': 0})
      >>> -3 - f
      Gamble({'a': '-41/10', 'c': -3, 'b': '-5/2'})

    * A gamble's domain can be cylindrically extended to the cartesian product
      of its domain and a specified :class:`~collections.Set`.

      >>> Gamble({'a': 0, 'b': -1}) ^ {'c', 'd'}
      Gamble({('b', 'c'): -1, ('a', 'd'): 0, ('a', 'c'): 0, ('b', 'd'): -1})

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
        >>> Gamble({}).bounds()
        (0, 0)

        """
        values = self.range()
        if values != frozenset():
            return (min(values), max(values))
        else:
            return (0, 0)

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


class Ray(Gamble):
    """Rays are the origin or directions in gamble space

    This class derives from :class:`~murasyp.gambles.Gamble`, so its methods
    apply here as well.

    What has changed:

    * Its domain coincides with its support and it is max-normalized.

      >>> Ray({'a': 5, 'b': -1, 'c': 0})
      Ray({'a': 1, 'b': '-1/5'})
      >>> Ray({'a': 0})
      Ray({})

    * Ray-arithmetic results in gambles (which can be converted to rays).

      >>> r = Ray({'a': 1,'b': -2})
      >>> r / 2
      Gamble({'a': '1/4', 'b': '-1/2'})
      >>> Ray(r * r)
      Ray({'a': '1/4', 'b': 1})

      .. warning::

        Currently, ray addition incorrectly returns rays:

        >>> r = Ray({'b', 'c'})
        >>> r + r
        Ray({'c': 1, 'b': 1})
        >>> 2 * r
        Gamble({'c': 2, 'b': 2})

    """

    def __init__(self, data):
        """Create a ray"""
        gamble = Gamble(data).normalized()
        if gamble == None:
            Gamble.__init__(self, {})
        else:
            Gamble.__init__(self, gamble | gamble.support())

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


class Cone(Set):
    """An immutable set of rays

      :type data: a :class:`~collections.Set` of arguments accepted by the
        :class:`~murasyp.gambles.Ray` constructor.

    Features:

    * There is an alternative constructor that accepts possibility spaces:

      >>> Cone(set('abc'))
      Cone(frozenset([Ray({'a': 1}), Ray({'b': 1}), Ray({'c': 1})]))

    """
    def __init__(self, data=frozenset()):
        """Create a set of desirable gambles"""
        if isinstance(data, Set):
            try:
                self._set = frozenset(Ray(element) for element in data)
            except:
                self._set = frozenset(Ray({element}) for element in data)
        else:
            raise TypeError("specify a Set instead of a " + type(data).__name__)

    __len__ = lambda self: self._set.__len__()
    __iter__ = lambda self: self._set.__iter__()
    __contains__ = lambda self: self._set.__contains__()
    __repr__ = lambda self: type(self).__name__ + '(' + repr(self._set) + ')'

    def domain(self):
        """The union of the domains of the element rays

          :returns: the possibility space of the cone, i.e., the union of the
            domains of the rays it contains
          :rtype: :class:`frozenset`

        >>> r = Ray({'a': .03, 'b': -.07})
        >>> s = Ray({'a': .07, 'c': -.03})
        >>> C = Cone(frozenset({r, s}))
        >>> C.domain()
        frozenset(['a', 'c', 'b'])

        """
        return frozenset.union(*(ray.domain() for ray in self))
