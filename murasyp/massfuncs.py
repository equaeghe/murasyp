from collections import Hashable
from itertools import repeat, izip
from murasyp import _RealValFunc
from murasyp.events import Event
from murasyp.gambles import Gamble

class MassFunc(_RealValFunc, Hashable):
    """An immutable, hashable real-valued function"""

    def __init__(self, data, number_type=None):
        """Create a mass function"""
        if isinstance(data, Event):
            data = dict(izip(data, repeat(1/self.make_number(len(data)))))
        return _RealValFunc.__init__(self, data, number_type)

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

    def __and__(self, other):
        """Scalar product

        >>> mf = MassFunc({'a': 2, 'b': 4, 'c': 8}, number_type='fraction')
        >>> A = Event(['a','b'])
        >>> mf & A
        Fraction(6, 1)
        >>> f = Gamble({'c': -5, 'd': 17})
        >>> mf & f
        -40.0

        """
        if isinstance(other, Event):
            return sum(self[x] for x in other)
        if isinstance(other, Gamble):
            return sum(self[x] * other[x] for x in self)

    _domain_joiner = lambda self, other: self.domain() | other.domain()

    def total_mass(self):
        """The total mass of the mass function

        >>> mf = MassFunc({'a': 2, 'b': 4, 'c': 8}, number_type='fraction')
        >>> mf.total_mass()
        Fraction(14, 1)

        """
        return sum(self.itervalues())

    def normalized(self):
        """Sum-norm normalized version of the mass function

        >>> mf = MassFunc({'a': 2, 'b': 4, 'c': 8}, number_type='fraction')
        >>> mf.normalized()
        (MassFunc({'a': Fraction(1, 7), 'c': Fraction(4, 7),
        ...        'b': Fraction(2, 7)}), Fraction(14, 1))

        """
        norm = self.total_mass()
        return ((1 / norm) * self, norm)

    def is_pmf(self):
        """Checks whether the mass function is a probability mass function

        >>> mf = MassFunc({'a': 2, 'b': 4, 'c': 8}, number_type='fraction')
        >>> mf.is_pmf()
        False
        >>> pmf, norm = mf.normalized()
        >>> pmf.is_pmf()
        True

        """
        return (self.total_mass() == 1 and min(self.itervalues()) >= 0)
