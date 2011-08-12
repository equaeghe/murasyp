from collections import Hashable
from murasyp.functions import Function
from murasyp.events import Event

class Vector(Function, Hashable):
    """Vectors are immutable, hashable rational-valued functions

      :param: a mapping (such as a :class:`dict`) to Rational values,
          i.e., :class:`~fractions.Fraction`. The fractions
          may be specified by giving an :class:`int`, a :class:`float` or in
          their :class:`str`-representation.
      :type: :class:`~collections.Mapping`

    This class derives from :class:`~murasyp.functions.Function`, so its
    methods apply here as well. This class's members are also hashable, which
    means they can be used as keys (in :class:`~collections.Set` and
    :class:`~collections.Mapping`, and their built-in variants :class:`set`
    and :class:`dict`). What has changed:

    * unspecified values are assumed to be zero;
    * the union of domains is used under pointwise operations;
    * a vector's domain can be restricted/extended to a specified
      :class:`~murasyp.events.Event`.

    >>> f = Vector({'a': 1.1, 'b': '-1/2','c': 0})
    >>> f
    Vector({'a': Fraction(11, 10), 'c': Fraction(0, 1), 'b': Fraction(-1, 2)})
    >>> f['d']
    0
    >>> g = Vector({'b': '.6', 'c': -2, 'd': 0.0})
    >>> (.3 * f - g) / 2
    Vector({'a': Fraction(33, 200), 'c': Fraction(1, 1), 'b': Fraction(-3, 8), 'd': Fraction(0, 1)})
    >>> f | Event({'a', 'b'})
    Vector({'a': Fraction(11, 10), 'b': Fraction(-1, 2)})
    >>> f | Event({'a', 'd'})
    Vector({'a': Fraction(11, 10), 'd': Fraction(0, 1)})

    """

    __getitem__ = lambda self, x: self._mapping[x] if x in self else 0
    __hash__ = lambda self: hash(tuple(item for item
                                            in self._mapping.iteritems()))

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

    def mass(self):
        """Sum of the values of the vector

          :returns: the sum of all values of the function
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
        Vector({'a': Fraction(2, 1), 'c': Fraction(0, 1), 'b': Fraction(-1, 1)})
        >>> Vector({'a': 1, 'b': -1,'c': 0}).sum_normalized() == None
        True

        .. note::

          ``None`` is returned in case the the sum of the vector's values is
          zero.

        """
        mass = self.mass()
        return None if mass == 0 else self / mass
