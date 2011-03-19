from collections import Hashable
from itertools import repeat, izip
from murasyp import RealValFunc
from murasyp.events import Event
from murasyp.gambles import Gamble

class MassFunc(RealValFunc, Hashable):
    """An immutable, hashable real-valued function"""

    def __init__(self, data, number_type=None):
        """Create a mass function"""
        if isinstance(data, Event):
            data = dict(izip(data, repeat(1/self.make_number(len(data)))))
        RealValFunc.__init__(self, data, number_type)
        if sum(self._mapping.itervalues()) == 0:
            raise ValueError("mass functions must have a nonzero total mass")

    __repr__ = lambda self: 'MassFunc(' + self._mapping.__repr__() + ')'

    def __getitem__(self, x):
        try:
            return self._mapping[x]
        except KeyError:
            return self.make_number(0)

    def pspace(self):
        """The mass function's possibility space"""
        return self.domain()

    def __hash__(self):
        return hash((self.domain,
                     tuple(self._mapping[x] for x in self.pspace())))

    def total_mass(self):
        """The total mass of the mass function

        >>> mf = MassFunc({'a': 2, 'b': 4, 'c': 8}, number_type='fraction')
        >>> mf.total_mass()
        Fraction(14, 1)

        """
        return sum(self.itervalues())

    def __or__(self, other):
        """Mass function conditional on the given event"""
        if not isinstance(other, Event):
            raise TypeError("the argument must be an Event")
        else:
            mass = sum(self[x] for x in other)
            if mass == 0:
                return None
            else:
                return MassFunc(dict((x, self[x] / mass) for x in other),
                                number_type=self.number_type)

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
        return r if r != None else min(other.itervalues())

    def __lshift__(self, other):
        r = self._weighted_sum(other)
        return r if r != None else max(other.itervalues())

    _domain_joiner = lambda self, other: self.domain() | other.domain()

    def normalized(self):
        """Total mass-normalized version of the mass function

        >>> mf = MassFunc({'a': 2, 'b': 4, 'c': 8}, number_type='fraction')
        >>> mf.normalized()
        (MassFunc({'a': Fraction(1, 7), 'c': Fraction(4, 7),
        ...        'b': Fraction(2, 7)}), Fraction(14, 1))

        """
        return (1 / self.total_mass()) * self

    def is_pmf(self):
        """Checks whether the mass function is a probability mass function

        >>> mf = MassFunc({'a': 2, 'b': 4, 'c': 8}, number_type='fraction')
        >>> mf.is_pmf()
        False
        >>> pmf, norm = mf.normalized()
        >>> pmf.is_pmf()
        True

        """
        return self.total_mass() == 1 and min(self.itervalues()) >= 0
