from collections import Mapping
from cdd import Matrix, RepType
from murasyp.massfuncs import PMFunc
from murasyp.gambles import Gamble, Ray
import murasyp.credalsets
import murasyp.mathprog

class CredalSet(set):
    """A set of probability mass functions

      :type `data`: a non-:class:`~collections.Mapping`
        :class:`~collections.Iterable` :class:`~collections.Container` of
        arguments accepted by the  :class:`~murasyp.massfuncs.PMFunc`
        constructor.

      >>> CredalSet('abc')
      CredalSet({PMFunc({'c': 1}), PMFunc({'b': 1}), PMFunc({'a': 1})})

    This class derives from :class:`~set`, so its methods apply here as
    well.

      .. todo::

        test all set methods and fix, or elegantly deal with, broken ones

    Additional and changed methods:

    * Lower and upper (conditional) expectations can be calculated, using the
      ``*`` and ``**`` operators, respectively.

      >>> p = PMFunc({'a': .03, 'b': .07, 'c': .9})
      >>> q = PMFunc({'a': .07, 'b': .03, 'c': .9})
      >>> K = CredalSet([p, q])
      >>> f = Gamble({'a': -1, 'b': 1, 'c': 0})
      >>> K * f
      Fraction(-1, 25)
      >>> K ** f
      Fraction(1, 25)
      >>> K * (f | f.support())
      Fraction(-2, 5)
      >>> K ** (f | f.support())
      Fraction(2, 5)

      .. note::

          The domain of the gamble determines the conditioning event.

    * They can be conditioned (each element :class:`~murasyp.massfuncs.PMFunc`
      is).

      >>> p = PMFunc({'a': .03, 'b': .07, 'c': .9})
      >>> q = PMFunc({'a': .07, 'b': .03, 'c': .9})
      >>> K = CredalSet([p, q])
      >>> f = Gamble({'a': -1, 'b': 1})
      >>> A = {'a','b'}
      >>> (K | A) * f
      Fraction(-2, 5)
      >>> (K | A) ** f
      Fraction(2, 5)

      This does not impede the classical union of sets.

      >>> CredalSet('a') | CredalSet('b')
      CredalSet({PMFunc({'b': 1}), PMFunc({'a': 1})})

    """
    def __init__(self, data=[]):
        """Initialize a credal set"""
        if isinstance(data, Mapping):
            raise TypeError(type(self) + " does not accept a mapping,"
                            + " but you passed it " + str(data))
        else:
            set.__init__(self, (PMFunc(element) for element in data))

    def add(self, data):
        """Add a probability mass function to the credal set

          :type `data`: arguments accepted by the
            :class:`~murasyp.massfuncs.PMFunc` constructor

        >>> K = CredalSet()
        >>> K
        CredalSet()
        >>> K.add({'a': .06, 'b': .14, 'c': 1.8, 'd': 0})
        >>> K
        CredalSet({PMFunc({'a': '3/100', 'c': '9/10', 'b': '7/100'})})

          .. todo::

            see whether all set functionality is carried over

        """
        set.add(self, PMFunc(data))

    def discard(self, data):
        """Remove a probability mass function from the credal set

          :type `data`: arguments accepted by the
            :class:`~murasyp.massfuncs.PMFunc` constructor

        >>> K = CredalSet('ab')
        >>> K
        CredalSet({PMFunc({'b': 1}), PMFunc({'a': 1})})
        >>> K.discard(PMFunc({'a'}))
        >>> K
        CredalSet({PMFunc({'b': 1})})

          .. todo::

            see whether all set functionality is carried over

        """
        set.discard(self, PMFunc(data))

    def __or__(self, other):
        """Credal set conditional on the given event"""
        if isinstance(other, CredalSet):
            return CredalSet(self.union(other))
        else:
            K = {p | other for p in self}
            if any(p == None for p in K):
                return type(self)(other)
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

          :returns: the possibility space of the credal set, i.e., the union of
              the domains of the probability mass functions it contains
          :rtype: :class:`frozenset`

        >>> p = PMFunc({'a': .03, 'b': .07})
        >>> q = PMFunc({'a': .07, 'c': .03})
        >>> K = CredalSet([p, q])
        >>> K.pspace()
        frozenset({'a', 'c', 'b'})

        """
        return frozenset.union(*(p.domain() for p in self))

    def discard_redundant(self):
        """Remove redundant elements from the credal set

        Redundant elements are those that are not vertices of the credal set's
        convex hull.

        >>> K = CredalSet('abc')
        >>> K.add({'a': 1, 'b': 1, 'c': 1})
        >>> K
        CredalSet({PMFunc({'c': 1}), PMFunc({'a': '1/3', 'c': '1/3', 'b': '1/3'}), PMFunc({'b': 1}), PMFunc({'a': 1})})
        >>> K.discard_redundant()
        >>> K
        CredalSet({PMFunc({'c': 1}), PMFunc({'b': 1}), PMFunc({'a': 1})})

        """
        pspace = list(self.pspace())
        K = list(self)
        mat = Matrix(list([1] + list(p[x] for x in pspace) for p in K),
                     number_type='fraction')
        mat.rep_type = RepType.GENERATOR
        lin, red = mat.canonicalize()
        for i in red:
            self.discard(K[i])

    def get_desir(self):
        """Generate the corresponding open set of desirable gambles

          :returns: the set of desirable gambles that corresponds as an
            uncertainty model
          :rtype: :class:`~murasyp.desirs.DesirSet`

        >>> CredalSet([PMFunc({'a', 'b'}), PMFunc({'c', 'b'}),
        ...            PMFunc({'a'}), PMFunc({'c'})]).get_desir()
        DesirSet({Cone({Ray({'a': 1, 'c': 1, 'b': -1}), Ray({'c': 1}), Ray({'b': 1}), Ray({'a': 1})})})

        """
        return murasyp.desirs.DesirSet([murasyp.mathprog.vf_enumeration(self)])
