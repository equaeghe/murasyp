from __future__ import division
from collections import Set, Hashable, Mapping, MutableMapping
from murasyp.functions import Function

class Vector(Function, Hashable):
    """Vectors map arguments to zero or a specified rational value

    This class derives from :class:`~murasyp.functions.Function`, so its
    methods apply here as well.

    What has changed:

    * This class's members are also hashable, which means they can be used as
      keys (in :class:`~collections.Set` and :class:`~collections.Mapping`, and
      their built-in variants :class:`set` and :class:`dict`).

      >>> {Function({})}
      Traceback (most recent call last):
        ...
      TypeError: unhashable type: 'Function'
      >>> assert {Vector({})} == {Vector({})}

    * Unspecified values are assumed to be zero.

      >>> f = Vector({'a': 1.1, 'b': '-1/2','c': 0})
      >>> assert f == Vector({'a': '11/10', 'c': 0, 'b': '-1/2'})
      >>> f['d']
      Fraction(0, 1)

    * The union of domains is used under pointwise operations.

      >>> f = Vector({'a': 1.1, 'b': '-1/2','c': 0})
      >>> g = Vector({'b': '.6', 'c': -2, 'd': 0.0})
      >>> assert (
      ...     1 + (.3 * f - g) / 2 ==
      ...     Vector({'a': '233/200', 'c': 2, 'b': '5/8', 'd': 1})
      ... )

    * A vector's domain can be restricted/extended to a specified
      :class:`~collections.Set`.

      >>> f = Vector({'a': 1.1, 'b': '-1/2','c': 0})
      >>> assert f | {'a','b'} == Vector({'a': '11/10', 'b': '-1/2'})
      >>> assert f | {'a','d'} == Vector({'a': '11/10', 'd': 0})

    """

    __getitem__ = lambda self, x: (self._mapping[x] if x in self
                                                    else self._make_rational(0))
    __hash__ = lambda self: hash(tuple(item for item
                                            in self._mapping.items()))

    _domain_joiner = lambda self, other: iter(self.domain() | other.domain())

    def __or__(self, other):
        """Restriction or extension with zero"""
        if isinstance(other, Set):
            return type(self)({x: self[x] for x in other})
        else:
            raise TypeError("the argument must be a Set")

    def mass(self):
        """Sum of the values of the vector

          :returns: the sum of all values of the vector
          :rtype: :class:`~fractions.Fraction`

        >>> Vector({'a': 1, 'b': '-1/2','c': 0}).mass()
        Fraction(1, 2)

        """
        return sum(self._mapping.values())

    def sum_normalized(self):
        """'Sum-of-values'-normalized version of the vector

          :returns: the gamble, but with its values divided by the sum of the
                    vector's values
          :rtype: :class:`~murasyp.vectors.Vector`

        >>> assert (
        ...     Vector({'a': 1, 'b': '-1/2','c': 0}).sum_normalized() ==
        ...     Vector({'a': 2, 'c': 0, 'b': -1})
        ... )
        >>> assert Vector({'a': 1, 'b': -1,'c': 0}).sum_normalized() == None

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
        return all(val >= 0 for val in self._mapping.values())


class Polytope(frozenset):
    """A frozenset of vectors

      :type `data`: a non-:class:`~collections.Mapping`
        :class:`~collections.Iterable` :class:`~collections.Container` of
        arguments accepted by the :class:`~murasyp.vectors.Vector` constructor.

      >>> assert (
      ...     Polytope([{'a': 2, 'b': 3}, {'b': 1, 'c': 4}]) ==
      ...     Polytope({Vector({'a': 2, 'b': 3}), Vector({'c': 4, 'b': 1})})
      ... )

    This class derives from :class:`~frozenset`, so its methods apply here as
    well.

      .. todo::

        test all set methods and fix, or elegantly deal with, broken ones

    Additional and changed methods:

    """
    def __new__(cls, data=[]):
        """Create a polytope"""
        if isinstance(data, Mapping):
            raise TypeError(str(cls) + " does not accept a mapping,"
                            + " but you passed it " + str(data))
        else:
            return frozenset.__new__(cls, (Vector(element) for element in data))

    def __init__(self, data=[]): # only here for Sphinx to pick up the argument
        """Initialize the polytope"""
        pass

    def domain(self):
        """The union of the domains of the element vectors

          :returns: the union of the domains of the vectors it contains
          :rtype: :class:`frozenset`

        >>> r = Vector({'a': .03, 'b': -.07})
        >>> s = Vector({'a': .07, 'c': -.03})
        >>> assert Polytope({r, s}).domain() == frozenset({'a', 'c', 'b'})

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
      >>> assert (
      ...     T << Vector({'a': 1, 'b': 2}) ==
      ...     Vector({('b', 'c'): 2, ('a', 'd'): 1,
      ...             ('a', 'c'): 1, ('b', 'd'): 2})
      ... )
      >>> P = Polytope({Vector({'a': -2})})
      >>> assert T << P == Polytope({Vector({('a', 'd'): -2, ('a', 'c'): -2})})

    """
    def __init__(self, mapping={}):
        """Create a transformation"""
        if isinstance(mapping, Mapping):
            self._mapping = {arg: Vector(value)
                             for arg, value in mapping.items()}
        else:
            raise TypeError("specify a mapping")

    __len__ = lambda self: len(self._mapping)
    __iter__ = lambda self: iter(self._mapping)
    __contains__ = lambda self, element: element in self._mapping
    __getitem__ = lambda self, element: self._mapping[element]

    def __setitem__(self, element, value):
        self._mapping.__setitem__(element, Vector(value))

    def __delitem__(self, element):
        mapping = self._mapping
        del mapping[element]

    def __lshift__(self, other):
        """Applying the transformation"""
        if isinstance(other, Vector):
            return sum(value * self[arg] for arg, value in other.items())
        if isinstance(other, Set):
            return type(other)(self << x for x in other)
        else:
            raise TypeError("the argument must be a Vector or a (nested) Set thereof")
