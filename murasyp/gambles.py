from collections import Hashable
from itertools import repeat, izip
from murasyp import _RealValFunc
from murasyp.events import Event

class Gamble(_RealValFunc, Hashable):
    """An immutable, hashable real-valued function"""

    def __init__(self, data, number_type=None):
        """Create a gamble"""
        if isinstance(data, Event):
          data = dict(izip(data, repeat(1)))
        return _RealValFunc.__init__(self, data, number_type)

    __repr__ = lambda self: 'Gamble(' + self._mapping.__repr__() + ')'

    def __getitem__(self, omega):
        try:
            return self._mapping[omega]
        except KeyError:
            return self.make_number(0)

    def __hash__(self):
        return hash((self.domain,
                     tuple(self._mapping[omega] for omega in self.pspace())))

    def pspace(self):
        """The gamble's possibility space"""
        return self.domain()

    def __mul__(self, other):
        if isinstance(other, Event):
            return type(self)(dict((omega, self[omega]) for omega in other),
                              self.number_type)
        else:
            return self._oper(other, '__mul__')

    __rmul__ = __mul__

    _domain_joiner = lambda self, other: self.domain() | other.domain()

    def norm(self):
        """The max-norm of the gamble

        :returns: the max-norm of the gamble
        :rtype: :class:`~cdd.NumberTypeable.NumberType`

        """
        return max(map(abs, self.range()))

    def normalized(self):
        """Max-norm normalized version of the gamble"""
        norm = self.norm()
        return ((1 / norm) * self, norm)

    def scaled_shifted(self):
        """Shifted and scaled version of the gamble"""
        values = self.range()
        shift = min(values)
        scale = max(values) - shift
        return ((1 / scale) * (self - shift), shift, scale)
