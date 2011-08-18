from collections import Set, MutableSet, Mapping
from cdd import Matrix, RepType
from murasyp.massfuncs import PMFunc
from murasyp.gambles import Gamble

class CredalSet(MutableSet):
    """A mutable set of probability mass functions

      :param: a :class:`~collections.Set` of :class:`~collections.Mapping`,
          each of which can be sum-normalized to a
          :class:`~murasyp.massfuncs.PMFunc`, i.e., it must be nonnegative and
          have nonzero total mass.
      :type: :class:`~collections.Set`

    Features:

    * There is an alternate constructor. If `data` is a
      :class:`~collections.Set` without :class:`~collections.Mapping`-members
      then a relative vacuous credal set is generated.

      >>> CredalSet(set('abc'))
      CredalSet(set([PMFunc({'a': 1}), PMFunc({'b': 1}), PMFunc({'c': 1})]))

    * Lower and upper expectations can be calculated, using the ``*`` and ``**``
      operators, respectively.

      >>> p = PMFunc({'a': .03, 'b': .07, 'c': .9})
      >>> q = PMFunc({'a': .07, 'b': .03, 'c': .9})
      >>> K = CredalSet({p, q})
      >>> f = Gamble({'a': -1, 'b': 1, 'c': 0})
      >>> K * f
      Fraction(-1, 25)
      >>> K ** f
      Fraction(1, 25)
      >>> K * (f | f.support())
      Fraction(-2, 5)
      >>> K ** (f | f.support())
      Fraction(2, 5)

    * They can be conditioned (each element :class:`~murasyp.massfuncs.PMFunc`
      is).

      >>> p = PMFunc({'a': .03, 'b': .07, 'c': .9})
      >>> q = PMFunc({'a': .07, 'b': .03, 'c': .9})
      >>> K = CredalSet({p, q})
      >>> f = Gamble({'a': -1, 'b': 1})
      >>> A = {'a','b'}
      >>> (K | A) * f
      Fraction(-2, 5)
      >>> (K | A) ** f
      Fraction(2, 5)

      This does not impede the classical union of sets.

      >>> CredalSet(set('a')) | CredalSet(set('b'))
      CredalSet(set([PMFunc({'a': 1}), PMFunc({'b': 1})]))

      .. warning::

        Most (all?) other set-operations are still broken.

    """

    def __init__(self, data=set([])):
        """Create a credal set"""
        if isinstance(data, Set):
            are_mappings = [isinstance(elem, Mapping) for elem in data]
            if all(are_mappings):
                self._set = set(PMFunc(mapping) for mapping in data)
            elif not any(are_mappings):
                self._set = set(PMFunc({x}) for x in data) # vacuous
            else:
                raise TypeError("either all or none of the elements of the "
                                + "specified Set " + str(data) + "must be "
                                + "Mappings")
        else:
            raise TypeError("specify a Set instead of a "
                            + type(data).__name__)

    __len__ = lambda self: self._set.__len__()
    __iter__ = lambda self: self._set.__iter__()
    __contains__ = lambda self: self._set.__contains__()
    __repr__ = lambda self: type(self).__name__ + '(' + repr(self._set) + ')'

    def add(self, mapping):
        """Add a probability mass function to the credal set

          :param: a mapping that can be sum-normalized to a
              :class:`~murasyp.massfuncs.PMFunc`, i.e., it must be nonnegative
              and have nonzero total mass.
          :type: :class:`~collections.Mapping`

        >>> K = CredalSet()
        >>> K
        CredalSet(set([]))
        >>> K.add({'a': .06, 'b': .14, 'c': 1.8, 'd': 0})
        >>> K
        CredalSet(set([PMFunc({'a': '3/100', 'c': '9/10', 'b': '7/100'})]))

        """
        self._set.add(PMFunc(mapping))

    def discard(self, mapping):
        """Remove a probability mass function from the credal set

          :param: a mapping that can be sum-normalized to a
              :class:`~murasyp.massfuncs.PMFunc`, i.e., it must be nonnegative
              and have nonzero total mass.
          :type: :class:`~collections.Mapping`

        >>> K = CredalSet({'a','b'})
        >>> K
        CredalSet(set([PMFunc({'a': 1}), PMFunc({'b': 1})]))
        >>> K.discard(PMFunc({'a'}))
        >>> K
        CredalSet(set([PMFunc({'b': 1})]))

        """
        self._set.discard(PMFunc(mapping))

    def __or__(self, other):
        """Credal set conditional on the given event"""
        if not isinstance(other, Set):
            raise TypeError(str(other) + " is not an Set")
        elif isinstance(other, CredalSet):
            return CredalSet(self._set | other._set)
        else:
            K = {p | other for p in self}
            if any(p == None for p in K):
                return type(self)({PMFunc({x}) for x in other})
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

        >>> p = PMFunc({'a': .03, 'b': .07})
        >>> q = PMFunc({'a': .07, 'c': .03})
        >>> K = CredalSet({p, q})
        >>> K.pspace()
        frozenset(['a', 'c', 'b'])

        """
        return frozenset.union(*(p.domain() for p in self))

    def discard_redundant(self):
        """Remove redundant elements from the credal set

        Redundant elements are those that are not vertices of the credal set's
        convex hull.

        >>> K = CredalSet(set('abc'))
        >>> K.add({'a': 1, 'b': 1, 'c': 1})
        >>> K
        CredalSet(set([..., PMFunc({'a': '1/3', 'c': '1/3', 'b': '1/3'})]))
        >>> K.discard_redundant()
        >>> K
        CredalSet(set([PMFunc({'a': 1}), PMFunc({'b': 1}), PMFunc({'c': 1})]))

        """
        pspace = list(self.pspace())
        K = list(self)
        mat = Matrix(list([1] + list(p[x] for x in pspace) for p in K),
                     number_type='fraction')
        mat.rep_type = RepType.GENERATOR
        lin, red = mat.canonicalize()
        for i in red:
            self.discard(K[i])
