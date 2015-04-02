from __future__ import division
from collections import Set, Mapping
from murasyp.vectors import Vector, Polytope

class Gamble(Vector):
    """Gambles map states to utility payoffs

    This class derives from :class:`~murasyp.vectors.Vector`, so its methods
    apply here as well.

    What has changed:

    * There is a new constructor. If `data` is not a
      :class:`~collections.Mapping`, but is a :class:`~collections.Iterable`
      :class:`~collections.Hashable` :class:`~collections.Container`, then its
      so-called indicator function is generated.

      >>> assert Gamble('abc') == Gamble({'a': 1, 'c': 1, 'b': 1})
      >>> assert Gamble({'abc'}) == Gamble({'abc': 1})

    * A gamble's domain can be cylindrically extended to the cartesian product
      of its domain and a specified :class:`~collections.Set`.

      >>> assert (
      ...     Gamble({'a': 0, 'b': -1}) ^ {'c', 'd'} ==
      ...     Gamble({('b', 'c'): -1, ('a', 'd'): 0,
      ...             ('a', 'c'): 0, ('b', 'd'): -1})
      ... )

    """

    def __init__(self, data={}):
        """Create a gamble"""
        if isinstance(data, Mapping):  # Hashable Mapping to Rational
            Vector.__init__(self, data)
        else: # indicator over Hashable Container
            Vector.__init__(self, {component: 1 for component in data})

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

        >>> assert (
        ...     Gamble({'a': 1, 'b': 3, 'c': 4}).scaled_shifted() ==
        ...     Gamble({'a': 0, 'c': 1, 'b': '2/3'})
        ... )

        .. note::

          ``None`` is returned in case the gamble is constant:

          >>> assert Gamble({'a': 2, 'b': 2}).scaled_shifted() == None

        """
        minval, maxval = self.bounds()
        return None if maxval == minval else (self - minval) / (maxval - minval)

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

        >>> assert (
        ...     Gamble({'a': 1, 'b': 3, 'c': 4}).normalized() ==
        ...     Gamble({'a': '1/4', 'c': 1, 'b': '3/4'})
        ... )

        .. note::

          ``None`` is returned in case the the gamble's norm is zero.

          >>> Gamble({'a': 0}).normalized() == None
          True

        """
        norm = self.norm()
        return None if norm == 0 else self / norm


class Ray(Gamble):
    """Rays directions in gamble space

    This class derives from :class:`~murasyp.gambles.Gamble`, so its methods
    apply here as well.

    What has changed:

    * Its domain coincides with its support and it is max-normalized.

      >>> assert Ray({'a': 5, 'b': -1, 'c': 0}) == Ray({'a': 1, 'b': '-1/5'})
      >>> assert Ray({'a': 0}) == Ray({})

    * Ray-arithmetic results in gambles (which can be converted to rays).

      >>> r = Ray({'a': 1,'b': -2})
      >>> assert .3 * r * r + r / 2 == Gamble({'a': '13/40', 'b': '-1/5'})

    """

    def __init__(self, data={}):
        """Create a ray"""
        gamble = Gamble(data).normalized()
        if gamble == None:
            Gamble.__init__(self, {})
        else:
            Gamble.__init__(self, gamble | gamble.support())

    __add__ = lambda self, other: Gamble(self) + other
    __radd__ = __add__

    __mul__ = lambda self, other: Gamble(self) * other
    __rmul__ = __mul__

    __truediv__ = lambda self, other: Gamble(self) / other


class Cone(Polytope):
    """A frozenset of rays

      :type `data`: a non-:class:`~collections.Mapping`
        :class:`~collections.Iterable` :class:`~collections.Container` of
        arguments accepted by the :class:`~murasyp.gambles.Ray` constructor.

      >>> assert (
      ...     Cone([{'a': 2, 'b': 3}, {'b': 1, 'c': 4}]) ==
      ...     Cone({Ray({'a': '2/3', 'b': 1}), Ray({'c': 1, 'b': '1/4'})})
      ... )
      >>> assert (
      ...     Cone('abc') ==
      ...     Cone({Ray({'a': 1}), Ray({'b': 1}), Ray({'c': 1})})
      ... )
      >>> assert (
      ...     Cone({'ab', 'bc'}) ==
      ...     Cone({Ray({'c': 1, 'b': 1}), Ray({'a': 1, 'b': 1})})
      ... )

    This class derives from :class:`~murasyp.vectors.Polytope`, so its methods
    apply here as well.

      .. todo::

        test all set methods and fix, or elegantly deal with, broken ones

    """
    def __new__(cls, data=[]):
        """Create a frozenset of rays"""
        if isinstance(data, Mapping):
            raise TypeError(str(cls) + " does not accept a mapping,"
                            + " but you passed it " + str(data))
        else:
            return frozenset.__new__(cls, (Ray(element) for element in data))

    def __init__(self, data=[]): # only here for Sphinx to pick up the argument
        """Initialize the cone"""
        pass
