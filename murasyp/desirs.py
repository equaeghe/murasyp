from collections import Mapping
from murasyp.gambles import Gamble, Ray, Cone
import murasyp.credalsets
import murasyp.mathprog

class DesirSet(set):
    """A set of cones

      :type `data`: a non-:class:`~collections.Mapping`
        :class:`~collections.Iterable` :class:`~collections.Container` of
        arguments accepted by the :class:`~murasyp.gambles.Cone` constructor.

      >>> DesirSet('abc')
      DesirSet({Cone({Ray({'a': 1})}), Cone({Ray({'b': 1})}), Cone({Ray({'c': 1})})})
      >>> DesirSet(['abc'])
      DesirSet({Cone({Ray({'c': 1}), Ray({'b': 1}), Ray({'a': 1})})})
      >>> DesirSet([['abc']])
      DesirSet({Cone({Ray({'a': 1, 'c': 1, 'b': 1})})})

    This class derives from :class:`~set`, so its methods apply here as
    well.

      .. todo::

        test all set methods and fix, or elegantly deal with, broken ones

    Additional and changed methods:

    * Lower and upper (conditional) expectations can be calculated, using the
      ``*`` and ``**`` operators, respectively.

      >>> D = DesirSet([[Gamble({'a': -1, 'c': '7/90'}),
      ...                Gamble({'a': 1, 'c': '-1/30'}),
      ...                Gamble({'a': -1, 'c': '1/9', 'b': -1}),
      ...                Gamble({'a': 1, 'c': '-1/9', 'b': 1})]])
      >>> f = Gamble({'a': -1, 'b': 1, 'c': 0})
      >>> D * f
      Fraction(-1, 25)
      >>> D ** f
      Fraction(1, 25)
      >>> D * (f | f.support())
      Fraction(-2, 5)
      >>> D ** (f | f.support())
      Fraction(2, 5)

      .. note::

          The domain of the gamble determines the conditioning event.

      We can deal with situations in which the gamble lies on a facet of the set
      of desirable gambles that corresponds to a conditioning event of (lower
      and/or upper) probability zero.

      >>> D = DesirSet()
      >>> D.set_pr('a', 1)
      >>> D * (Gamble('c') | {'b', 'c'})
      0
      >>> D * (Gamble('c') | {'a', 'b', 'c'})
      0
      >>> D.set_pr(Gamble('b') | {'b', 'c'}, '1/2')
      >>> D * (Gamble('c') | {'b', 'c'})
      Fraction(1, 2)

    """
    def __init__(self, data=[]):
        """Initialize a set of desirable gambles"""
        if isinstance(data, Mapping):
            raise TypeError(type(self) + " does not accept a mapping,"
                            + " but you passed it " + str(data))
        else:
            set.__init__(self, (Cone(element) for element in data))

    def add(self, data):
        """Add a cone to the set of desirable gambles

          :type `data`: arguments accepted by the :class:`~murasyp.gambles.Cone`
            constructor

        >>> D = DesirSet()
        >>> D
        DesirSet()
        >>> D.add([Gamble({'a': -.06, 'b': .14, 'c': 1.8, 'd': 0})])
        >>> D
        DesirSet({Cone({Ray({'a': '-1/30', 'c': 1, 'b': '7/90'})})})

          .. todo::

            see whether all set functionality is carried over

        """
        set.add(self, Cone(data))

    def discard(self, data):
        """Remove a cone from the set of desirable gambles

          :type `data`: arguments accepted by the :class:`~murasyp.gambles.Cone`
            constructor

        >>> D = DesirSet({'a','b'})
        >>> D
        DesirSet({Cone({Ray({'a': 1})}), Cone({Ray({'b': 1})})})
        >>> D.discard([Ray({'a'})])
        >>> D
        DesirSet({Cone({Ray({'b': 1})})})

          .. todo::

            see whether all set functionality is carried over

        """
        set.discard(self, frozenset(Ray(element) for element in data))

    def pspace(self):
        """The possibility space of the set of desirable gambles

          :returns: the possibility space of the set of desirable gambles, i.e.,
            the union of the domains of the cones it contains
          :rtype: :class:`frozenset`

        >>> D = DesirSet(['abc'])
        >>> r = Ray({'c': .03, 'd': -.07})
        >>> s = Ray({'a': .07, 'e': -.03})
        >>> D.add([r, s])
        >>> D.pspace()
        frozenset({'a', 'c', 'b', 'e', 'd'})

        """
        return frozenset.union(*(cone.domain() for cone in self))

    def set_lower_pr(self, data, val):
        """Set the lower probability/prevision (expectation) of an event/gamble

          :arg `data`: the gamble for which a probability/prevision value is given
          :type `data`: arguments accepted by the :class:`~murasyp.gambles.Gamble`
            constructor
          :arg `val`: the probability/prevision value
          :type `val`: a representation of :class:`~numbers.Real`

        The nontrivial cone corresponing to the prevision specification is
        calculated and added to the set of desirable gambles.

        >>> D = DesirSet()
        >>> D.set_lower_pr(Gamble({'a', 'b'}) | {'a', 'b', 'c'}, .4)
        >>> D
        DesirSet({Cone({Ray({'a': 1, 'c': '-2/3', 'b': 1}), Ray({'a': 1, 'c': 1, 'b': 1})})})

        .. note::

          The domain of the input gamble determines the conditioning event.

        """
        gamble = Gamble(data)
        self.add({gamble - gamble._make_rational(val), Ray(gamble.domain())})

    def set_upper_pr(self, data, val):
        """Set the upper probability/prevision (expectation) of an event/gamble

          :arg `data`: the gamble for which a probability/prevision value is given
          :type `data`: arguments accepted by the :class:`~murasyp.gambles.Gamble`
            constructor
          :arg `val`: the probability/prevision value
          :type `val`: a representation of :class:`~numbers.Real`

        The nontrivial cone corresponing to the prevision specification is
        calculated and added to the set of desirable gambles.

        >>> D = DesirSet()
        >>> D.set_upper_pr(Gamble({'a', 'b'}) | {'a', 'b', 'c'}, .4)
        >>> D
        DesirSet({Cone({Ray({'a': -1, 'c': '2/3', 'b': -1}), Ray({'a': 1, 'c': 1, 'b': 1})})})

        .. note::

          The domain of the input gamble determines the conditioning event.

        """
        gamble = Gamble(data)
        self.set_lower_pr(-gamble, -gamble._make_rational(val))

    def set_pr(self, data, val):
        """Set the probability/prevision (expectation) of an event/gamble

          :arg `data`: the gamble for which a probability/prevision value is given
          :type `data`: arguments accepted by the :class:`~murasyp.gambles.Gamble`
            constructor
          :arg `val`: the probability/prevision value
          :type `val`: a representation of :class:`~numbers.Real`

        This is identical to setting the lower and upper prevision to the same
        value.

        >>> D = DesirSet()
        >>> D.set_pr(Gamble({'a', 'b'}) | {'a', 'b', 'c'}, .4)
        >>> D
        DesirSet({Cone({Ray({'a': -1, 'c': '2/3', 'b': -1}), Ray({'a': 1, 'c': 1, 'b': 1})}), Cone({Ray({'a': 1, 'c': '-2/3', 'b': 1}), Ray({'a': 1, 'c': 1, 'b': 1})})})

        .. note::

          The domain of the input gamble determines the conditioning event.

        """
        self.set_lower_pr(data, val)
        self.set_upper_pr(data, val)

    def asl(self):
        """Check whether the set of desirable gambles avoids sure loss

          :rtype: :class:`bool`

        A set of desirable gambles does not avoid sure loss if and only if some
        nonnegative linear combination of desirable gambles is everywhere
        negative.

        >>> D = DesirSet()
        >>> D.add([{'a': -1, 'b': -1, 'c': 1}])
        >>> D.add([{'a': 1, 'b': -1, 'c': -1}])
        >>> D.asl()
        True
        >>> D.add([{'a': -1, 'b': 1, 'c': -1}])
        >>> D.asl()
        False
        >>> D = DesirSet('ab')
        >>> D.add([{'b': -1}])
        >>> D.asl()
        True

        """
        D = DesirSet([Cone.union(*(self | DesirSet([self.pspace()])))])
        return murasyp.mathprog.feasible(D) == set()

    def apl(self):
        """Check whether the set of desirable gambles avoids partial loss

          :rtype: :class:`bool`

        A set of desirable gambles does not avoid partial loss if and only if
        some nonnegative linear combination of desirable gambles is everywhere
        nonpositive and somewhere negative.

        >>> D = DesirSet()
        >>> D.add([{'a': -1, 'b': -1, 'c': 1}])
        >>> D.apl()
        True
        >>> D.add([{'a': -1, 'b': 1, 'c': -1}])
        >>> D.apl()
        False

        We can deal correctly with non-closed sets of desirable gambles, i.e.,
        containing non-singleton cones:

        >>> D = DesirSet()
        >>> D.set_pr(Gamble('b') | {'a', 'b'}, 0)
        >>> D
        DesirSet({Cone({Ray({'a': 1, 'b': 1}), Ray({'b': 1})}), Cone({Ray({'a': 1, 'b': 1}), Ray({'b': -1})})})
        >>> D.apl()
        True

        """
        D = self | DesirSet(self.pspace())
        return murasyp.mathprog.feasible(D) == set()

    def __mul__(self, other):
        """Lower expectation of a gamble"""
        gamble = Gamble(other)
        indicator = Gamble(gamble.domain())
        return murasyp.mathprog.maximize(
                  self | DesirSet(self.pspace() | gamble.domain()
                                                | indicator.domain())
                       | DesirSet([{indicator}, {-indicator}, {()}]),
                  gamble, (0, {indicator: 1, -indicator: -1}))

    def __pow__(self, other):
        """Upper expectation of a gamble"""
        return - self.__mul__(- other)

    def get_credal(self):
        """Generate the corresponding (closed) credal set

          :returns: the (closed) credal set that corresponds as an uncertainty
            model
          :rtype: :class:`~murasyp.credalsets.CredalSet`

        >>> D = DesirSet(['abc'])
        >>> D.set_lower_pr({'a': 1, 'b': 0, 'c': 1}, .5)
        >>> D.get_credal()
        CredalSet({PMFunc({'a': '1/2', 'b': '1/2'}), PMFunc({'c': '1/2', 'b': '1/2'}), PMFunc({'a': 1}), PMFunc({'c': 1})})

        """
        C = Cone.union(*self)
        return murasyp.credalsets.CredalSet(murasyp.mathprog.vf_enumeration(C))

