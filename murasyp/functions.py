from collections import Mapping, MutableMapping, Hashable
from fractions import Fraction
from murasyp import _make_rational

class Function(Hashable, MutableMapping):
    """Rational-valued functions

      :type `mapping`: :class:`~collections.Mapping` (such as a :class:`dict`)
        to a representation of :class:`~numbers.Real`
      :type `frozen`: :class:`~bool`

    This class is implemented as a :class:`~collections.Hashable` 
    :class:`~collections.MutableMapping`; its mutability can be controlled using
    the `frozen` parameter and the :meth:`~murasyp.functions.Function.freeze`
    and :meth:`~murasyp.functions.Function.thaw` methods.

    Features:

    * Values may be specified as :class:`int`, :class:`float`, or
      :class:`~fractions.Fraction`, whose :class:`str`-representation is then
      especially convenient.

      >>> f = Function({'a': 11e-1, 'b': '-1/2', 'c': 0}); f
      Function({'a': '11/10', 'c': 0, 'b': '-1/2'})
      >>> f['a']
      Fraction(11, 10)

      .. note::

        No floats are ever really used; they are immediately converted to
        fractions and should be seen as just a convenient input representation
        for decimal numbers.

    * If `frozen=True`, the :class:`~murasyp.functions.Function` is effectively 
      immutable:

      >>> f = Function({})
      >>> f['a'] = 3
      Traceback (most recent call last):
        ...
      TypeError: frozen functions are immutable

      If `frozen=False`, the :class:`~murasyp.functions.Function` is effectively 
      mutable:

      >>> f = Function({'a': -1}, False)
      >>> f['a'] = 5; f['b'] = 2; f
      Function({'a': 5, 'b': 2})
      >>> del f['a']; f
      Function({'b': 2})
      >>> f.clear(); f
      Function({})

      However, strange things may happen if mutable objects are used as keys in
      :class:`~collections.Set` or :class:`~collections.Mapping`:

      >>> f = Function({}, False) # frozen=False
      >>> g = Function({}) # so frozen=True by default
      >>> f == g # only content matters for equality, not mutability
      True
      >>> S = {f}; S
      {Function({})}
      >>> (f in S) & (g in S)
      True
      >>> f['a'] = 1; S
      {Function({'a': 1})}
      >>> (f in S) | (g in S)
      False

      So it is good practice to :meth:`~murasyp.functions.Function.freeze` a
      :class:`~murasyp.functions.Function` before using it as a key.

    * Scalar multiplication and division, as well as pointwise multiplication,
      addition, and subtraction (also with scalars) is possible.

      >>> f = Function({'a': 1.1, 'b': '-1/2','c': 0})
      >>> g = Function({'b': '.6', 'c': -2, 'd': 0.0})
      >>> -1 + (.3 * f - g) / 2
      Function({'c': 0, 'b': '-11/8'})
      >>> f * g
      Function({'c': 0, 'b': '-3/10'})

      .. note::

        The domain of results of sums and differences is the intersection of
        the respective domains.

    """

    def __init__(self, mapping={}, frozen=True):
        """Create a rational-valued function"""
        self._mapping = {arg: _make_rational(value)
                         for arg, value in mapping.items()}
        self._frozen = frozen
        self._normless_type = type(self)

    __len__ = lambda self: len(self._mapping)
    __iter__ = lambda self: iter(self._mapping)
    __contains__ = lambda self, arg: arg in self._mapping
    __getitem__ = lambda self, arg: self._mapping[arg]
    __hash__ = lambda self: hash(frozenset(self.items()))

    def __setitem__(self, arg, value):
        if self._frozen:
            raise TypeError("frozen functions are immutable")
        else:
            self._mapping.__setitem__(arg, _make_rational(value))

    def __delitem__(self, arg):
        if self._frozen:
            raise TypeError("frozen functions are immutable.")
        else:
            self._mapping.__delitem__(arg)

    def __repr__(self):
        """Return a readable unambiguous string representation"""
        return type(self).__name__ + '(' + str(self) + ')'

    def __str__(self):
        """Return a readable string representation"""
        return ('{' +
                ', '.join(repr(arg) + ': ' +
                          (repr(str(val)) if '/' in str(val) else str(val))
                          for arg, val in self.items()) +
                '}')

    def freeze(self):
        """Freeze the function, i.e., make it effectively immutable

        >>> f = Function({}, False)
        >>> f['a'] = 1; f
        Function({'a': 1})
        >>> f.freeze()
        >>> f['b'] = 2; f
        Traceback (most recent call last):
          ...
        TypeError: frozen functions are immutable
        Function({'a': 1})

        """
        self._frozen = True

    def thaw(self):
        """Thaw the function, i.e., make it effectively mutable

        >>> f = Function({}, True)
        >>> f['a'] = 1; f
        Traceback (most recent call last):
          ...
        TypeError: frozen functions are immutable
        Function({})
        >>> f.thaw()
        >>> f['b'] = 2; f
        Function({'b': 2})

        """
        if self._frozen == None:
            raise TypeError(repr(self) + " cannot be thawed")
        else:
            self._frozen = False

    def domain(self):
        """Domain of the function

          :returns: the domain of the function, i.e., those values for which the
                    function is defined
          :rtype: :class:`frozenset`

        >>> Function({'a': 1, 'b': -1, 'c': 0}).domain()
        frozenset({'a', 'c', 'b'})

        """
        return frozenset(self.keys())

    def range(self):
        """Range of the function

          :returns: the range of the function, i.e., the set of all values
                    returned by the function
          :rtype: :class:`frozenset`

        >>> Function({'a': 1, 'b': -1, 'c': 0}).range()
        frozenset({Fraction(0, 1), Fraction(1, 1), Fraction(-1, 1)})

        """
        return frozenset(self.values())

    def support(self):
        """Support of the function

          :returns: the support of the function, i.e., that part of the domain
                    for which the function is nonzero
          :rtype: :class:`frozenset`

        >>> Function({'a': 1, 'b': -1, 'c': 0}).support()
        frozenset({'a', 'b'})

        """
        return frozenset(arg for arg, value in self.items() if value != 0)

    def _with_scalar(self, other, operator):
        """Application of a binary operator to a function/scalar-pair"""
        try:
            return self._normless_type({arg: operator(value,
                                                      _make_rational(other))
                                        for arg, value in self.items()})
        except NotImplementedError:
            raise

    def _with_function(self, other, operator):
        """pointwise application of a binary operator to a pair of functions"""
        if isinstance(other, type(self)):
            return self._normless_type({arg: operator(self[arg], other[arg])
                                        for arg in self._domain_joiner(other)})
        else:
            raise NotImplementedError

    _domain_joiner = lambda self, other: iter(self.domain() & other.domain())

    def _pointwise(self, other, operator):
        """Pointwise application of a binary operator"""
        try:
            return self._with_function(other, operator)
        except:
            return self._with_scalar(other, operator)

    __add__ = lambda self, other: self._pointwise(other, Fraction.__add__)
    __radd__ = __add__

    __mul__ = lambda self, other: self._pointwise(other, Fraction.__mul__)
    __rmul__ = __mul__

    def __truediv__(self, other):
        return self._with_scalar(other, Fraction.__truediv__)

    __neg__ = lambda self: self * (-1)

    __sub__ = lambda self, other: self + (-other)
    __rsub__ = lambda self, other: -(self - other)
