from collections import Set, MutableSet
from murasyp.events import Event
from murasyp.gambles import Gamble
from murasyp.massassignments import MassAssignment

class CredalSet(MutableSet):
    """A mutable set of mass functions"""

    def __init__(self, data=set([])):
        """Create a credal set"""
        if isinstance(data, Event):
            self._set = set(MassAssignment(set(x)) for x in data) # vacuous
        elif isinstance(data, Set) and all(isinstance(x, MassAssignment)
                                           and x.is_pmf() for x in data):
            self._set = set(data)
        else:
            raise TypeError('specify an even or a set of mass functions')

    __repr__ = lambda self: type(self).__name__ + '(' + repr(self._set) + ')'

    def add(self, pmf):
        """Add a probability mass function to the credal set"""
        if isinstance(pmf, MassAssignment) and pmf.is_pmf():
            self._set.add(pmf)
        else:
            raise TypeError('specify a mass function')

    def discard(self, pmf):
        """Remove a probability mass function from the credal set"""
        return self._set.discard(pmf)

    def __or__(self, other):
        """Credal set conditional on the given event"""
        if not isinstance(other, Event):
            raise TypeError("the argument must be an Event")
        else:
            pmfs = set(pmf | other for pmf in self)
            if any(pmf == None for pmf in pmfs):
                return type(self)(set(MassAssignment(set(x)) for x in other))
            else:
                return type(self)(mfs)

    def __mult__(self, other):
        """Lower expectation of gamble"""
        return NotImplementedError

    def __pow__(self, other):
        """Upper expectation of gamble"""
        return NotImplementedError