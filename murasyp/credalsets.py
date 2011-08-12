from collections import Set, MutableSet
from murasyp.probmassfuncs import ProbMassFunc
from murasyp.gambles import Gamble

class CredalSet(MutableSet):
    """A mutable set of probability mass functions

      :param: a :class:`~collections.Set` of
          :class:`~murasyp.probmassfuncs.ProbMassFunc` or an
          :class:`~collections.Set` (such as a :class:`dict`);
          in the latter case, a relative vacuous credal set is generated.
      :type: :class:`~collections.MutableSet`

    Members behave like any :class:`set`, Moreover, they can be conditioned
    just as :class:`~murasyp.probmassfuncs.ProbMassFunc` are and lower and
    upper expectations can be calculated, using the ``*`` and ``**`` operators,
    respectively.

    >>> p = ProbMassFunc({'a': .03, 'b': .07, 'c': .9})
    >>> q = ProbMassFunc({'a': .07, 'b': .03, 'c': .9})
    >>> K = CredalSet({p, q})
    >>> K
    CredalSet(set([ProbMassFunc({'a': Fraction(7, 100), 'c': Fraction(9, 10), 'b': Fraction(3, 100)}), ProbMassFunc({'a': Fraction(3, 100), 'c': Fraction(9, 10), 'b': Fraction(7, 100)})]))
    >>> f = Gamble({'a': -1, 'b': 1})
    >>> K * f
    Fraction(-1, 25)
    >>> K ** f
    Fraction(1, 25)
    >>> A = {'a','b'}
    >>> (K | A) * f
    Fraction(-2, 5)
    >>> (K | A) ** f
    Fraction(2, 5)

    """

    def __init__(self, data=set([])):
        """Create a credal set"""
        if isinstance(data, Set):
            if all(isinstance(p, ProbMassFunc) for p in data):
                self._set = set(data)
            else:
                self._set = set(ProbMassFunc({x}) for x in data) # vacuous
        else:
            raise TypeError("specify an event or a set "
                            + "of probability mass functions")

    __len__ = lambda self: self._set.__len__()
    __iter__ = lambda self: self._set.__iter__()
    __contains__ = lambda self: self._set.__contains__()
    __repr__ = lambda self: type(self).__name__ + '(' + repr(self._set) + ')'

    def add(self, p):
        """Add a probability mass function to the credal set

        >>> K = CredalSet()
        >>> K
        CredalSet(set([]))
        >>> p = ProbMassFunc({'a': .03, 'b': .07, 'c': .9})
        >>> K.add(p)
        >>> K
        CredalSet(set([ProbMassFunc({'a': Fraction(3, 100), 'c': Fraction(9, 10), 'b': Fraction(7, 100)})]))

        """
        if isinstance(p, ProbMassFunc) and p.is_pmf():
            self._set.add(p)
        else:
            raise TypeError(str(p) + " is not a probability mass function")

    def discard(self, p):
        """Remove a probability mass function from the credal set

        >>> K = CredalSet({'a','b'})
        >>> K
        CredalSet(set([ProbMassFunc({'a': Fraction(1, 1)}), ProbMassFunc({'b': Fraction(1, 1)})]))
        >>> K.discard(ProbMassFunc({'a'}))
        >>> K
        CredalSet(set([ProbMassFunc({'b': Fraction(1, 1)})]))

        """
        return self._set.discard(p)

    def __or__(self, other):
        """Credal set conditional on the given event"""
        if not isinstance(other, Set):
            raise TypeError(str(other) + " is not an Set")
        else:
            K = {p | other for p in self}
            if any(p == None for p in K):
                return type(self)({ProbMassFunc({x}) for x in other})
            else:
                return type(self)(K)

    def __mul__(self, other):
        """Lower expectation of a gamble"""
        if isinstance(other, Gamble):
            if len(self) == 0:
                raise Error("Empty credal sets have no expectations")
            else:
                return min(p * other for p in self)
        else:
            raise TypeError(str(other) + " is not a gamble")

    def __pow__(self, other):
        """Upper expectation of a gamble"""
        if isinstance(other, Gamble):
            if len(self) == 0:
                raise Error("Empty credal sets have no expectations")
            else:
                return max(p * other for p in self)
        else:
            raise TypeError(str(other) + " is not a gamble")
