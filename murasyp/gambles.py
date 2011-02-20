from collections import Hashable
from murasyp import _RealValFunc

class Gamble(_RealValFunc, Hashable):
    """An immutable, hashable real-valued function"""

    __init__ = _RealValFunc.__init__
    __repr__ = lambda self: 'Gamble(' + dict(self).__repr__() + ')'

    # TODO: default missing values to 0

    def __hash__(self):
        return hash((self.domain,
                     tuple(self._mapping[omega] for omega in self.pspace())))

    pspace = lambda self: self.domain()

    _domain_joiner = lambda self, other: self.domain() | other.domain()

    def norm(self):
        """The max-norm of the gamble"""
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
        return ((1 / scale) * (self - minimum), shift, scale)
