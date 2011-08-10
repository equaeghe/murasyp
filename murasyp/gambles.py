from collections import Hashable
from itertools import repeat
from murasyp import _make_real, RealValFunc
from murasyp.events import Event

class Gamble(RealValFunc, Hashable):
    """Gambles are immutable, hashable real-valued functions

      :param: a mapping (such as a :class:`dict`) to real values,
          i.e., :class:`~numbers.Real`, which includes the built-in types
          :class:`float` and :class:`int`, but also
          :class:`~fractions.Fraction`, which can be used for exact
          arithmetic. The fractions may be given in their
          :class:`str`-representation.
      :type: :class:`~collections.Mapping`

    This class derives from :class:`~murasyp.RealValFunc`, so its methods
    apply here as well. This class's members are also hashable, which means
    they can be used as keys (in :class:`~collections.Set` and
    :class:`~collections.Mapping`, and their built-in variants :class:`set`
    and :class:`dict`). What has changed:

    * pointwise multiplication and scalar addition & subtraction has been added;
    * how domains are combined under pointwise operations;
    * unspecified values are assumed to be zero.

    >>> f = Gamble({'a': 1.1, 'b': '-1/2','c': 0})
    >>> f['d']
    0
    >>> f
    Gamble({'a': 1.1, 'c': 0, 'b': Fraction(-1, 2)})
    >>> g = Gamble({'b': '.6', 'c': -2, 'd': 0.0})
    >>> g
    Gamble({'c': -2, 'b': Fraction(3, 5), 'd': 0.0})
    >>> (.3 * f - g) / 2
    Gamble({'a': 0.165, 'c': 1.0, 'b': -0.375, 'd': 0.0})
    >>> f * g
    Gamble({'a': 0.0, 'c': 0, 'b': Fraction(-3, 10), 'd': 0.0})
    >>> -3 - f
    Gamble({'a': -4.1, 'c': -3, 'b': Fraction(-5, 2)})

    .. note::

      Notice that the domain of results of sums and differences is the
      union of the respective domains.

    Furthermore, gambles can be combined with events:

    * for restriction and extension of their domain;
    * for cylindrical extension to a cartesian-product domain.

    >>> f = Gamble({'a': 1.1, 'b': '-1/2','c': 0})
    >>> f | Event({'a', 'b'})
    Gamble({'a': 1.1, 'b': Fraction(-1, 2)})
    >>> f | Event({'a', 'd'})
    Gamble({'a': 1.1, 'd': 0})
    >>> f ^ Event({'e', 'f'})
    Gamble({('c', 'f'): 0, ('a', 'f'): 1.1, ('a', 'e'): 1.1,
    ...     ('b', 'f'): Fraction(-1, 2), ('b', 'e'): Fraction(-1, 2),
    ...     ('c', 'e'): 0})

    Additionally, gambles' properties and related gambles are computed by
    calling the appropriate methods. Their possibility spaces coincide with
    their domain.

    """

    def __init__(self, data):
        """Create a gamble"""
        if isinstance(data, Event):
            data = dict(zip(data, repeat(1)))
        RealValFunc.__init__(self, data)

    __getitem__ = lambda self, x: self._mapping[x] if x in self else 0
    __hash__ = lambda self: hash(self._mapping)

    def pspace(self):
        """The gamble's possibility space

          :returns: the gamble's possibility space
          :rtype: :class:`frozenset`

        >>> h = Gamble({'a': 1, 'b': 3, 'c': 4})
        >>> h.pspace()
        frozenset({'a', 'c', 'b'})

        """
        return self.domain()

    def __add__(self, other):
        """Also allow addition of real-valued functions and scalars"""
        if isinstance(other, Gamble):
            return RealValFunc.__add__(self, other)
        else:
            other = _make_real(other)
            return type(self)(dict((arg, value + other) for arg, value
                                                        in self.items()))

    __radd__ = __add__
    __rsub__ = lambda self, other: -(self - other)

    def __mul__(self, other):
        """Pointwise multiplication of real-valued functions"""
        if isinstance(other, Gamble):
            return type(self)(dict((x, self[x] * other[x])
                                   for x in self._domain_joiner(other)))
        else:
            return RealValFunc.__mul__(self, other)

    def _domain_joiner(self, other):
        if type(self) == type(other):
            return iter(self.domain() | other.domain())
        else:
            raise TypeError("cannot combine domains of objects with different"
                            "types: '" + type(self).__name__ + "' and '"
                                       + type(other).__name__ + "'")

    def __or__(self, other):
        """Restriction or extension with zero"""
        if isinstance(other, Event):
            return type(self)(dict((x, self[x]) for x in other))
        else:
            raise("the argument must be an Event")

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
          :rtype: a pair (:class:`tuple`) of :class:`~numbers.Real`

        >>> h = Gamble({'a': 1, 'b': 3, 'c': 4})
        >>> h.bounds()
        (1, 4)

        """
        values = self.range()
        return (min(values), max(values))

    def scaled_shifted(self):
        """Shifted and scaled version of the gamble

          :returns: a scaled and shifted version 
                    :math:`(f-\min f)/(\max f-\min f)` of the gamble :math:`f`
          :rtype: :class:`~murasyp.Gamble`

        >>> h = Gamble({'a': 1, 'b': 3, 'c': 4})
        >>> h.scaled_shifted()
        Gamble({'a': 0.0, 'c': 1.0, 'b': 0.6666666666666666})

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
          :rtype: :class:`~numbers.Real`

        >>> h = Gamble({'a': 1, 'b': 3, 'c': 4})
        >>> h.norm()
        4

        """
        minval, maxval = self.bounds()
        return max(-minval, maxval)

    def normalized(self):
        """Max-norm normalized version of the gamble

          :returns: a normalized version :math:`f/\|f\|_\infty` of the gamble
                    :math:`f`
          :rtype: :class:`~murasyp.Gamble`

        >>> h = Gamble({'a': 1, 'b': 3, 'c': 4})
        >>> h.normalized()
        Gamble({'a': 0.25, 'c': 1.0, 'b': 0.75})

        .. note::

          The gamble itself is returned in case it is identically zero.

        """
        norm = self.norm()
        return self if norm == 0 else self / norm
