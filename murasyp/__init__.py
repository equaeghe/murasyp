__version__ = '0.1'
__release__ = __version__

from cdd import NumberTypeable, get_number_type_from_sequences
from collections import Mapping

class RealValFunc(Mapping, NumberTypeable):
    """A real-valued function"""

    def __init__(self, mapping, number_type=None):
        """Create a real-valued function

        :param mapping: a mapping to real values.
        :type data: |collections.Mapping|
        :param number_type: The type to use for numbers:
            ``'float'`` or ``'fraction'``. If omitted,
            then :func:`~cdd.get_number_type_from_sequences`
            is used to determine the number type.
        :type number_type: :class:`str`
        """
        if isinstance(mapping, Mapping):
            if number_type is None:
                NumberTypeable.__init__(self,
                    get_number_type_from_sequences(mapping.itervalues()))
            else:
                NumberTypeable.__init__(self, number_type)
            self._mapping = dict((element, self.make_number(value))
                                 for element, value in mapping.iteritems())
        else:
            raise TypeError('specify a mapping')

    @classmethod
    def _make(cls, mapping):
        return mapping if isinstance(mapping, cls) else cls(mapping)

    __len__ = lambda self: len(self._mapping)
    __iter__ = lambda self: iter(self._mapping)
    __contains__ = lambda self, element: element in self._mapping
    __getitem__ = lambda self, element: self._mapping[element]
    __repr__ = lambda self: 'RealValFunc(' + self._mapping.__repr__() + ')'
    __str__ = lambda self: self._mapping.__str__()

    domain = lambda self: frozenset(self.keys())
    range = lambda self: frozenset(self.values())

    def support(self):
      return frozenset(element for element, value
                               in self.iteritems() if value != 0)

    __add__ = lambda self, other: self._oper(other, '__add__')
    __radd__ = __add__
    __sub__ = lambda self, other: self._oper(other, '__sub__')
    __rsub__ = lambda self, other: -(self - other)
    __mul__ = lambda self, other: self._oper(other, '__mul__')
    __rmul__ = __mul__
    __truediv__ = lambda self, other: self._oper(other, '__truediv__')
    __rtruediv__ = lambda self, other: (self / other) ** (-1)
    __neg__ = lambda self: self * (-1)
    __pow__ = lambda self, other: self._oper(other, '__pow__')

    def _oper(self, other, oper_str):
        oper = getattr(self.NumberType, oper_str)
        if isinstance(other, RealValFunc):
            return self._pointwise(other, oper)
        else:
            return self._scalar(other, oper)

    def _pointwise(self, other, oper):
        if self.number_type != other.number_type:
            raise ValueError("number type mismatch")
        return type(self)(dict((arg, oper(self[arg], other[arg]))
                               for arg in self._domain_joiner(other)),
                          number_type=self.number_type)

    _domain_joiner = lambda self, other: self.domain() & other.domain()

    def _scalar(self, other, oper):
        other = self.make_number(other)
        return type(self)(dict((arg, oper(value, other))
                               for arg, value in self.iteritems()),
                          number_type=self.number_type)
