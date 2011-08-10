from collections import Hashable
from itertools import repeat
from murasyp import RealValFunc
from murasyp.events import Event
from murasyp.gambles import Gamble

class MassFunc(RealValFunc, Hashable):
    """An immutable, hashable real-valued function"""

    def __init__(self, data):
        """Create a mass function"""
        if isinstance(data, Event):
            data = dict(zip(data, repeat(1 / len(data))))
        RealValFunc.__init__(self, data)
        if sum(self._mapping.values()) == 0:
            raise ValueError("mass functions must have a nonzero total mass")

    __getitem__ = lambda self, x: self._mapping[x] if x in self else 0
    __hash__ = lambda self: hash(self._mapping)

    def pspace(self):
        """The mass function's possibility space"""
        return self.domain()

    def total_mass(self):
        """The total mass of the mass function

        >>> mf = MassFunc({'a': 2, 'b': 4, 'c': 8})
        >>> mf.total_mass()
        14

        """
        return sum(self.values())

    def __or__(self, other):
        """Mass function conditional on the given event"""
        if not isinstance(other, Event):
            raise TypeError("the argument must be an Event")
        else:
            mass = sum(self[x] for x in other)
            if mass == 0:
                return None
            else:
                return type(self)(dict((x, self[x] / mass) for x in other))

    def _weighted_sum(self, other):
        """Calculates the self-weighted sum of other"""
        if not isinstance(other, (Event, Gamble)):
            raise TypeError("the argument must be an Event or a Gamble")
        else:
            if self.number_type != other.number_type:
                raise ValueError("number type mismatch")
            else:
                if other.pspace() >= self.pspace():
                    return sum(self[x] * other[x] for x in self)
                else:
                    mf = self | other.pspace()
                    if mf == None:
                        None
                    else:
                        return sum(mf[x] * other[x] for x in mf)

    def __lshift__(self, other):
        r = self._weighted_sum(other)
        return r if r != None else min(other.values())

    def __lshift__(self, other):
        r = self._weighted_sum(other)
        return r if r != None else max(other.values())

    _domain_joiner = lambda self, other: self.domain() | other.domain()

    def normalized(self):
        """Total mass-normalized version of the mass function

        >>> mf = MassFunc({'a': 2, 'b': 4, 'c': 8})
        >>> mf.normalized()
        (MassFunc({'a': Fraction(1, 7), 'c': Fraction(4, 7),
        ...        'b': Fraction(2, 7)}), Fraction(14, 1))

        """
        return self / self.total_mass()

    def is_pmf(self):
        """Checks whether the mass function is a probability mass function

        >>> mf = MassFunc({'a': 2, 'b': 4, 'c': 8})
        >>> mf.is_pmf()
        False
        >>> pmf, norm = mf.normalized()
        >>> pmf.is_pmf()
        True

        """
        return self.total_mass() == 1 and min(self.itervalues()) >= 0
