from collections import Set, Mapping, MutableMapping
from murasyp.functions import _Function, Function, frozenFunction

class _Vector(_Function):
    """Vector (base class)"""

    def __init__(self, mapping={}):
        """Create a vector"""
        super().__init__(mapping)
        self._base_type = _Vector
        self._arith_type = frozenVector

    __getitem__ = lambda self, x: (self._mapping[x] if x in self._mapping
                                                    else self._make_rational(0))

    _domain_joiner = lambda self, other: iter(self.domain() | other.domain())

    def __or__(self, other):
        """Restriction or extension with zero"""
        return self._arith_type({x: self[x] for x in other})

    def mass(self):
        """Sum of the values of the vector

          :returns: the sum of all values of the vector
          :rtype: :class:`~fractions.Fraction`

        >>> Vector({'a': 1, 'b': '-1/2','c': 0}).mass()
        Fraction(1, 2)

        """
        return sum(self.values())

    def sum_normalized(self):
        """'Sum-of-values'-normalized version of the vector

          :returns: the gamble, but with its values divided by the sum of the
                    vector's values
          :rtype: :class:`~murasyp.vectors.Vector`

        >>> Vector({'a': 1, 'b': '-1/2','c': 0}).sum_normalized()
        frozenVector({'a': 2, 'c': 0, 'b': -1})
        >>> Vector({'a': 1, 'b': -1,'c': 0}).sum_normalized() == None
        True

        .. note::

          ``None`` is returned in case the the sum of the vector's values is
          zero.

        """
        mass = self.mass()
        return None if mass == 0 else self / mass

    def is_nonnegative(self):
        """Checks whether all values are nonnegative

          :returns: the truth value of the statement
          :rtype: :class:`~bool`

        >>> Vector({'a': 1.6, 'b': -.6}).is_nonnegative()
        False
        >>> Vector({'a': .4, 'b': .6}).is_nonnegative()
        True

        """
        return all(val >= 0 for val in self.values())


class Vector(_Vector, Function):
    """Rational-valued functions assumed to be zero outside of their domain

    This class derives from :class:`~murasyp.functions.Function`, so its
    methods apply here as well.

    What has changed:

    * Unspecified values are assumed to be zero.

      >>> f = Vector({'a': 1.1, 'b': '-1/2','c': 0})
      >>> f
      Vector({'a': '11/10', 'c': 0, 'b': '-1/2'})
      >>> f['d']
      Fraction(0, 1)

    * The union of domains is used under pointwise operations.

      >>> f = Vector({'a': 1.1, 'b': '-1/2','c': 0})
      >>> g = Vector({'b': '.6', 'c': -2, 'd': 0.0})
      >>> 1 + (.3 * f - g) / 2
      frozenVector({'a': '233/200', 'c': 2, 'b': '5/8', 'd': 1})

    * A vector's domain can be restricted/extended to the elements of a
      specified :class:`~collections.Iterable`.

      >>> f = Vector({'a': 1.1, 'b': '-1/2','c': 0})
      >>> f | 'ab'
      frozenVector({'a': '11/10', 'b': '-1/2'})
      >>> f | 'ad'
      frozenVector({'a': '11/10', 'd': 0})

    """


class frozenVector(_Vector, frozenFunction):
    """Frozen vectors

    This class is the immutable cousin of :class:`~murasyp.vectors.Vector`.
    It shares most of its functionality and relates to it in the same way that
    :class:`~murasyp.functions.frozenFunction` relates to 
    :class:`~murasyp.functions.Function`.

    """

class Polytope(frozenset):
    """A frozenset of vectors

      :type `data`: an :class:`~collections.Iterable` over arguments accepted by
        the :class:`~murasyp.vectors.Vector` constructor.

      >>> Polytope([{'a': 2, 'b': 3}, {'b': 1, 'c': 4}])
      Polytope({frozenVector({'c': 4, 'b': 1}), frozenVector({'a': 2, 'b': 3})})

    This class derives from :class:`~frozenset`, so its methods apply here as
    well.

      .. todo::

        test all set methods and fix, or elegantly deal with, broken ones

    Additional and changed methods:

    """
    def __new__(cls, data=[]):
        """Create a polytope"""
        return frozenset.__new__(cls, (frozenVector(element)
                                       for element in data))

    def __init__(self, data=[]): # only here for Sphinx to pick up the argument
        """Initialize the polytope"""
        pass

    def domain(self):
        """The union of the domains of the element vectors

          :returns: the union of the domains of the vectors it contains
          :rtype: :class:`frozenset`

        >>> r = Vector({'a': .03, 'b': -.07})
        >>> s = Vector({'a': .07, 'c': -.03})
        >>> Polytope([r, s]).domain()
        frozenset({'a', 'c', 'b'})

        """
        return frozenset.union(*(vector.domain() for vector in self))


class Trafo(MutableMapping):
    """A linear transformation between vector spaces

      :type `mapping`: a :class:`~collections.Mapping` (such as a :class:`dict`)
        of arguments accepted by the :class:`~murasyp.vectors.Vector`
        constructor.

    Features:

    * The transformation can be applied to :class:`~murasyp.vectors.Vector`
      (and :class:`~collections.Set` thereof) using the ``<<`` operator:

      >>> T = Trafo()
      >>> T['a'] = {('a', 'c'): 1, ('a', 'd'): 1}
      >>> T['b'] = {('b', 'c'): 1, ('b', 'd'): 1}
      >>> T << Vector({'a': 1, 'b': 2})
      frozenVector({('b', 'c'): 2, ('a', 'd'): 1, ('a', 'c'): 1, ('b', 'd'): 2})
      >>> P = Polytope([Vector({'a': -2})])
      >>> T << P
      Polytope({frozenVector({('a', 'd'): -2, ('a', 'c'): -2})})

    """
    def __init__(self, mapping={}):
        """Create a transformation"""
        if isinstance(mapping, Mapping):
            self._mapping = {arg: frozenVector(value)
                             for arg, value in mapping.items()}
        else:
            raise TypeError("specify a mapping")

    __len__ = lambda self: len(self._mapping)
    __iter__ = lambda self: iter(self._mapping)
    __contains__ = lambda self, element: element in self._mapping
    __getitem__ = lambda self, element: self._mapping[element]

    def __setitem__(self, element, value):
        self._mapping.__setitem__(element, frozenVector(value))

    def __delitem__(self, element):
        mapping = self._mapping
        del mapping[element]

    def __lshift__(self, other):
        """Applying the transformation"""
        if isinstance(other, _Vector):
            return sum(value * self[arg] for arg, value in other.items())
        if isinstance(other, Set):
            return type(other)(self << x for x in other)
        else:
            raise TypeError("the argument must be a Vector or a (nested) Set thereof")
