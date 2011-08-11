from itertools import repeat
from murasyp.vectors import Vector
from murasyp.events import Event
from murasyp.gambles import Gamble

class MassAssignment(Vector):
    """(Unit) mass assignments are immutable, hashable rational-valued
    functions with values that sum to one.

      :param: a mapping (such as a :class:`dict`) to Rational values,
          i.e., :class:`~numbers.Rational`, which includes the built-in type
          :class:`int`, but also :class:`~fractions.Fraction`. The fractions
          may be given as a :class:`float` or in their
          :class:`str`-representation. The sum of the values must be nonzero.
      :type: :class:`~collections.Mapping`

    This class derives from :class:`~murasyp.vectors.Vector`, so its methods
    apply here as well. What has changed:

    * its total mass, i.e., sum of values, has to be nonzero;
    * restriction becomes conditioning, i.e., it includes renormalization and
      may be impossible if the conditioning event has zero net mass assigned.

    """

    def __init__(self, data):
        """Create a mass function"""
        if isinstance(data, Event):
            data = dict(zip(data, repeat(1 / len(data))))
        Vector.__init__(self, data)
        if self.mass() != 1:
            raise ValueError("mass assignment must have a total mass of 1")

    def __or__(self, other):
        """Mass function conditional on the given event

        >>> print('add doctest')
        add doctest

        """
        return (Vector(self) | other).normalized()

    def __mult__(self, other):
        """Weighted sum of mass assignment and ***

        """

    def is_pmf(self):
        """Checks whether the mass assignment is a probability mass function

        >>> print('add doctest')
        add doctest

        """
        return all(self._mapping.itervalues()) >= 0
