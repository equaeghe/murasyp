from collections import Set, MutableSet
from murasyp.events import Event
from murasyp.gambles import Gamble
from murasyp.massfuncs import MassFunc

class MassFuncSet(MutableSet):
    """A mutable set of mass functions"""

    def __init__(self, set=set([])):
        """Create a set of mass functions"""
        if isinstance(set, Set) and all(isinstance(x, MassFunc) for x in set):
            self._set = set(set)
        else:
            raise TypeError('specify a set of mass functions')

    __repr__ = lambda self: type(self).__name__ + '(' + repr(self._set) + ')'

    def add(self, mf):
        """Add a mass functions to the set of mass functions"""
        if isinstance(mf, MassFunc):
            self._set.add(mf)
        else:
            raise TypeError('specify a mass function')

    discard = lambda self, mf: self._set.discard(mf)

    def __or__(self, other):
        """Mass function set conditional on the given event"""
        if not isinstance(other, Event):
            raise TypeError("the argument must be an Event")
        else:
            mfs = set(mf | other for mf in self)
            if any(mf == None for mf in mfs):
                return type(self)(set(MassFunc(set[x]) for x in other))
            else:
                return type(self)(mfs)

    def __lshift__(self, other):
        rs = [self._weighted_sum(mf) for mf in self]
        if any(r == None for r in rs):
            return min(other.values())
        else:
          min(rs)

    def __rshift__(self, other):
        rs = [self._weighted_sum(mf) for mf in self]
        if any(r == None for r in rs):
            return max(other.values())
        else:
          max(rs)

    def normalized(self):
        """Set of sum-normalized version of the mass functions in the set

        >>> mf = MassFunc({'a': 2, 'b': 4, 'c': 8})
        >>> mf.normalized()
        (MassFunc({'a': Fraction(1, 7), 'c': Fraction(4, 7),
        ...        'b': Fraction(2, 7)}), Fraction(14, 1))

        """
        return type(self)(set(mf.normalized() for mf in self))

    def is_credal_set(self):
        """Checks whether the mass function set is a credal set"""
        return all(mf.is_pmf for mf in self)
