from collections import Set, Hashable
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
      >>> {Vector({})}
      set([Vector({})])

    * Unspecified values are assumed to be zero.

      >>> f = Vector({'a': 1.1, 'b': '-1/2','c': 0})
      >>> f
      Vector({'a': '11/10', 'c': 0, 'b': '-1/2'})
      >>> f['d']
      0

    * The union of domains is used under pointwise operations.

      >>> f = Vector({'a': 1.1, 'b': '-1/2','c': 0})
      >>> g = Vector({'b': '.6', 'c': -2, 'd': 0.0})
      >>> (.3 * f - g) / 2
      Vector({'a': '33/200', 'c': 1, 'b': '-3/8', 'd': 0})

    * A vector's domain can be restricted/extended to a specified
      :class:`~collections.Set`.

      >>> f = Vector({'a': 1.1, 'b': '-1/2','c': 0})
      >>> f | {'a','b'}
      Vector({'a': '11/10', 'b': '-1/2'})
      >>> f | {'a','d'}
      Vector({'a': '11/10', 'd': 0})

    """

    __getitem__ = lambda self, x: self._mapping[x] if x in self else 0
    __hash__ = lambda self: hash(tuple(item for item
                                            in self._mapping.iteritems()))

    def _domain_joiner(self, other):
        if type(self) == type(other):
            return iter(self.domain() | other.domain())
        else:
            raise TypeError("cannot combine domains of objects with different "
                            "types: '" + type(self).__name__ + "' and '"
                                       + type(other).__name__ + "'")

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
        return sum(self._mapping.itervalues())

    def sum_normalized(self):
        """'Sum-of-values'-normalized version of the vector

          :returns: the gamble, but with its values divided by the sum of the
                    vector's values
          :rtype: :class:`~murasyp.vectors.Vector`

        >>> Vector({'a': 1, 'b': '-1/2','c': 0}).sum_normalized()
        Vector({'a': 2, 'c': 0, 'b': -1})
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
        return all(val >= 0 for val in self._mapping.itervalues())
