from collections import Set, MutableSet
from murasyp.events import Event
from murasyp.gambles import Gamble
from murasyp.massfuncs import MassFunc

class MassFuncSet(MutableSet):
      """A mutable set of mass functions"""

      def __init__(self, set=set([])):
          """Create a set of mass functions"""
          if isinstance(set, Set) && all(isinstance(x, MassFunc) for x in set):
              self._set = set(set)
          else:
              raise TypeError('specify a set of mass functions')

      def add(self, mass_func):
          """Add a mass functions to the set of mass functions"""
          if isinstance(mass_func, MassFunc):
              self._set.add(mass_func)
          else:
              raise TypeError('specify a mass function')

      discard = lambda self, mass_func: self._set.discard(mass_func)

      def __and__(self, other):
          if isinstance(other, Event) or isinstance(other, Gamble):
          else:
            