from collections import Set, MutableSet
from murasyp.gambles import Gamble
from murasyp.rays import Ray

class AlmostDesir(MutableSet):
    """A mutable set of rays"""

    def __init__(self, data=set([])):
        """Create a set of almost desirable gambles"""
        if isinstance(data, Set):
            if all(isinstance(f, Gamble) for f in data):
                self._set = set(Ray(f) for f in data)
                self.pspace = set().union(f.domain() for f in self._set)
            else:
                self.pspace = set(data)
                self._set = set(Ray({x}) for x in self.pspace) # vacuous
        else:
            raise TypeError("specify an event or a set of gambles")
