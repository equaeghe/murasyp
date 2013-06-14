from collections import Mapping
from murasyp.vectors import Vector, Polytope

class Gamble(Vector):
    """Gambles map states to utility payoffs

    This class derives from :class:`~murasyp.vectors.Vector`, so its methods
    apply here as well.

    What has changed:

    * There is a new constructor. If `data` is not a
      :class:`~collections.Mapping`, but is a :class:`~collections.Iterable`,
      then its so-called indicator function is generated.

      >>> Gamble('abc')
      Gamble({'a': 1, 'c': 1, 'b': 1})
      >>> Gamble(['abc'])
      Gamble({'abc': 1})

    * A gamble's domain can be cylindrically extended to the cartesian product
      of its domain and a specified :class:`~collections.Iterable`.

      >>> Gamble({'a': 0, 'b': -1}) ^ 'cd'
      Gamble({('b', 'c'): -1, ('a', 'd'): 0, ('a', 'c'): 0, ('b', 'd'): -1})

    """

    def __init__(self, data={}, frozen=True):
        """Create a gamble"""
        if not isinstance(data, Mapping):  # assume representation of an event
          data = {component: 1 for component in data}
        super().__init__(data)
        self._normless_type = Gamble

    def __xor__(self, other):
        """Cylindrical extension"""
        return self._normless_type({(x, y): self[x] for x in self
                                                    for y in other})

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

          ``None`` is returned in case the gamble is constant:

          >>> Gamble({'a': 2, 'b': 2}).scaled_shifted() == None
          True

        """
        minval, maxval = self.bounds()
        return None if maxval == minval else (self - minval) / (maxval - minval)


class Ray(Gamble):
    """Rays are directions in gamble space

    This class derives from :class:`~murasyp.gambles.Gamble`, so its methods
    apply here as well. Rays are permanently frozen to guarantee that
    normalization is preserved.

    What has changed:

    * Its domain coincides with its support and it is max-normalized.

      >>> Ray({'a': 5, 'b': -1, 'c': 0})
      Ray({'a': 1, 'b': '-1/5'})
      >>> Ray({'a': 0})
      Ray({})

    * Thawing a ray is disallowed:

      >>> Ray({}).thaw()
      Traceback (most recent call last):
        ...
      TypeError: normalized functions cannot be thawed

      For the same reason, ray-arithmetic results in gambles (which can be
      converted to rays):

      >>> r = Ray({'a': 1,'b': -2})
      >>> .3 * r * r + r / 2
      Gamble({'a': '13/40', 'b': '-1/5'})

    """

    def __init__(self, data={}):
        """Create a ray"""
        gamble = Gamble(data).max_normalized()
        super().__init__(gamble | gamble.support())


class Cone(Polytope):
    """A frozenset of rays

      :type `data`: an :class:`~collections.Iterable` of arguments accepted by
        the :class:`~murasyp.gambles.Ray` constructor.

    >>> Cone([{'a': 2, 'b': 3}, {'b': 1, 'c': 4}])
    Cone({Ray({'c': 1, 'b': '1/4'}), Ray({'a': '2/3', 'b': 1})})
    >>> Cone('abc')
    Cone({Ray({'c': 1}), Ray({'b': 1}), Ray({'a': 1})})
    >>> Cone({'ab', 'bc'})
    Cone({Ray({'a': 1, 'b': 1}), Ray({'c': 1, 'b': 1})})

    This class derives from :class:`~murasyp.vectors.Polytope`, so its methods
    apply here as well.

    .. todo::

      test all set methods and fix, or elegantly deal with, broken ones

    """
    def __new__(cls, data=[]):
        """Create a frozenset of rays"""
        return frozenset.__new__(cls, (Ray(element) for element in data))

    def __init__(self, data=[]): # only here for Sphinx to pick up the argument
        """Initialize the cone"""
        pass
