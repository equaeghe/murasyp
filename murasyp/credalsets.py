from collections import Set, MutableSet
from cdd import Matrix, RepType
from murasyp.probmassfuncs import ProbMassFunc
from murasyp.gambles import Gamble

class CredalSet(MutableSet):
    """A mutable set of probability mass functions

      :param: a :class:`~collections.Set` of
          :class:`~murasyp.probmassfuncs.ProbMassFunc` or an
          :class:`~collections.Set` (such as a :class:`dict`);
          in the latter case, a relative vacuous credal set is generated.
      :type: :class:`~collections.MutableSet`

    Members behave like any :class:`set`, Moreover, they can be conditioned
    just as :class:`~murasyp.probmassfuncs.ProbMassFunc` are and lower and
    upper expectations can be calculated, using the ``*`` and ``**`` operators,
    respectively.

    >>> p = ProbMassFunc({'a': .03, 'b': .07, 'c': .9})
    >>> q = ProbMassFunc({'a': .07, 'b': .03, 'c': .9})
    >>> K = CredalSet({p, q})
    >>> K
    CredalSet(set([ProbMassFunc({'a': '7/100', 'c': '9/10', 'b': '3/100'}), ProbMassFunc({'a': '3/100', 'c': '9/10', 'b': '7/100'})]))
    >>> f = Gamble({'a': -1, 'b': 1})
    >>> K * f
    Fraction(-1, 25)
    >>> K ** f
    Fraction(1, 25)
    >>> A = {'a','b'}
    >>> (K | A) * f
    Fraction(-2, 5)
    >>> (K | A) ** f
    Fraction(2, 5)

    """

    def __init__(self, data=set([])):
        """Create a credal set"""
        if isinstance(data, Set):
            if all(isinstance(p, ProbMassFunc) for p in data):
                self._set = set(data)
            else:
                self._set = set(ProbMassFunc({x}) for x in data) # vacuous
        else:
            raise TypeError("specify an event or a set "
                            + "of probability mass functions")

    __len__ = lambda self: self._set.__len__()
    __iter__ = lambda self: self._set.__iter__()
    __contains__ = lambda self: self._set.__contains__()
    __repr__ = lambda self: type(self).__name__ + '(' + repr(self._set) + ')'

    def add(self, p):
        """Add a probability mass function to the credal set

          :param: a mapping (such as a :class:`dict`) to *nonnegative* Rational
              values, i.e., :class:`~fractions.Fraction`. The fractions
              may be specified by giving an :class:`int`, a :class:`float` or in
              their :class:`str`-representation. Sum-normalization is applied.
          :type: :class:`~collections.Mapping`

        >>> K = CredalSet()
        >>> K
        CredalSet(set([]))
        >>> p = ProbMassFunc({'a': .06, 'b': .14, 'c': 1.8, 'd': 0})
        >>> K.add(p)
        >>> K
        CredalSet(set([ProbMassFunc({'a': '3/100', 'c': '9/10', 'b': '7/100'})]))

        """
        self._set.add(ProbMassFunc(p))

    def discard(self, p):
        """Remove a probability mass function from the credal set

          :param: a probability mass function
          :type: :class:`~murasyp.ProbMassFunc`

        >>> K = CredalSet({'a','b'})
        >>> K
        CredalSet(set([ProbMassFunc({'a': 1}), ProbMassFunc({'b': 1})]))
        >>> K.discard(ProbMassFunc({'a'}))
        >>> K
        CredalSet(set([ProbMassFunc({'b': 1})]))

        """
        self._set.discard(p)

    def __or__(self, other):
        """Credal set conditional on the given event"""
        if not isinstance(other, Set):
            raise TypeError(str(other) + " is not an Set")
        else:
            K = {p | other for p in self}
            if any(p == None for p in K):
                return type(self)({ProbMassFunc({x}) for x in other})
            else:
                return type(self)(K)

    def __mul__(self, other):
        """Lower expectation of a gamble"""
        if isinstance(other, Gamble):
            if len(self) == 0:
                raise Error("Empty credal sets have no expectations")
            else:
                return min(p * other for p in self)
        else:
            raise TypeError(str(other) + " is not a gamble")

    def __pow__(self, other):
        """Upper expectation of a gamble"""
        if isinstance(other, Gamble):
            if len(self) == 0:
                raise Error("Empty credal sets have no expectations")
            else:
                return max(p * other for p in self)
        else:
            raise TypeError(str(other) + " is not a gamble")

    def pspace(self):
        """The possibility space of the credal set

        >>> p = ProbMassFunc({'a': .03, 'b': .07})
        >>> q = ProbMassFunc({'a': .07, 'c': .03})
        >>> K = CredalSet({p, q})
        >>> K.pspace()
        frozenset(['a', 'c', 'b'])

        """
        return frozenset.union(*(p.domain() for p in self))

    def discard_redundant(self):
        """Remove redundant elements of the credal set

        Redundant elements are those that do not belong to the set of vertices
        of the convex hull of the credal set.

        >>> K = CredalSet(set('abc'))
        >>> K
        CredalSet(set([ProbMassFunc({'a': 1}), ProbMassFunc({'b': 1}), ProbMassFunc({'c': 1})]))
        >>> K.add({'a': '1/3', 'b': '1/3', 'c': '1/3'})
        >>> K
        CredalSet(set([ProbMassFunc({'a': 1}), ProbMassFunc({'b': 1}), ProbMassFunc({'c': 1}), ProbMassFunc({'a': '1/3', 'c': '1/3', 'b': '1/3'})]))
        >>> K.discard_redundant()
        >>> K
        CredalSet(set([ProbMassFunc({'a': 1}), ProbMassFunc({'b': 1}), ProbMassFunc({'c': 1})]))

        """
        pspace = list(self.pspace())
        K = list(self)
        mat = Matrix(list(list(p[x] for x in pspace) for p in K),
                     number_type='fraction')
        mat.rep_type = RepType.GENERATOR
        lin, red = mat.canonicalize()
        for i in red:
            self.discard(K[i])
