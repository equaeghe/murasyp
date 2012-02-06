from collections import Set, MutableSet, Mapping
from cdd import Matrix, LPObjType, LinProg, LPStatusType, RepType, Polyhedron
from murasyp import _make_rational
from murasyp.gambles import Gamble, Ray, DiRay
from murasyp.massfuncs import PMFunc

class DesirSet(MutableSet):
    """A mutable set of dirays

      :type data: a :class:`~collections.Set` of objects accepted by the
        :class:`~murasyp.gambles.DiRay` constructor.

    Features:

    * There is alternative constructor that accepts possibility spaces as well:

      >>> DesirSet(set('abc'))
      DesirSet(set([DiRay({'a': 1}, {}), DiRay({'b': 1}, {}), ...]))

    * Lower and upper (conditional) expectations can be calculated, using the
      ``*`` and ``**`` operators, respectively.

      >>> D = DesirSet(set([Gamble({'a': -1, 'c': '7/90'}),
      ...                   Gamble({'a': 1, 'c': '-1/30'}),
      ...                   Gamble({'a': -1, 'c': '1/9', 'b': -1}),
      ...                   Gamble({'a': 1, 'c': '-1/9', 'b': 1})]))
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

      .. warning::

        Does not take the second tier ray of constituent dirays into account,
        as it should. So it may give an incorrect answer.

    """
    def __init__(self, data=set([])):
        """Create a set of desirable gambles"""
        if isinstance(data, Set):
            try:
                self._set = set(DiRay(element) for element in data)
            except:
                self._set = set(DiRay({element}) for element in data)
        else:
            raise TypeError("specify a Set instead of a "
                            + type(data).__name__)

    def add(self, data):
        """Add a diray to the set of desirable gambles

          :type data: arguments accepted by the :class:`~murasyp.gambles.DiRay`
            constructor

        >>> D = DesirSet()
        >>> D
        DesirSet(set([]))
        >>> D.add({'a': -.06, 'b': .14, 'c': 1.8, 'd': 0})
        >>> D
        DesirSet(set([DiRay({'a': '-1/30', 'c': 1, 'b': '7/90'}, {})]))

        """
        self._set.add(DiRay(data))

    def discard(self, data):
        """Remove a diray from the credal set

          :type data: arguments accepted by the :class:`~murasyp.gambles.DiRay`
            constructor

        >>> D = DesirSet({'a','b'})
        >>> D
        DesirSet(set([DiRay({'a': 1}, {}), DiRay({'b': 1}, {})]))
        >>> D.discard(Ray({'a'}))
        >>> D
        DesirSet(set([DiRay({'b': 1}, {})]))

        """
        self._set.discard(DiRay(data))

    __len__ = lambda self: self._set.__len__()
    __iter__ = lambda self: self._set.__iter__()
    __contains__ = lambda self: self._set.__contains__()
    __repr__ = lambda self: type(self).__name__ + '(' + repr(self._set) + ')'

    def pspace(self):
        """The possibility space of the set of desirable gambles

          :returns: the possibility space of the set of desirable gambles, i.e.,
            the union of the domains of the dirays it contains
          :rtype: :class:`frozenset`

        >>> r = Ray({'a': .03, 'b': -.07})
        >>> s = Ray({'a': .07, 'c': -.03})
        >>> D = DesirSet({r, s})
        >>> D.pspace()
        frozenset(['a', 'c', 'b'])

        """
        return frozenset.union(*(diray.domain() | diray.dir.domain()
                                 for diray in self))

    def discard_redundant(self):
        """Remove redundant elements from the set of desirable gambles

        Redundant elements are those that are not extreme rays of set of
        desirable gambles's convex conical hull.

        >>> D = DesirSet(set('abc'))
        >>> D.add({'a': 1, 'b': 1, 'c': 1})
        >>> D
        DesirSet(set([DiRay({'a': 1, 'c': 1, 'b': 1}, {}), ...]))
        >>> D.discard_redundant()
        >>> D
        DesirSet(set([DiRay({'a': 1}, {}), DiRay({'b': 1}, {}), DiRay({'c': 1}, {})]))

        Because we use dirays, we can make sure we do not discard rays that do
        not belong to the convex hull of the set of desirable gambles but that
        do belong to its convex closure.

        >>> D = DesirSet(set([DiRay({'b'}, {'c'}), DiRay({'a'}, {'c'}),
        ...                   DiRay({'a': 1, 'b': 1}, {})]))
        >>> D.discard_redundant()
        >>> D
        DesirSet(set([DiRay({'a': 1, 'b': 1}, {}), ...]))

        """
        pspace = list(self.pspace())
        D = list(self)
        mat = Matrix(list([0] + list(ray[x] for x in pspace) +
                                list(ray.dir[x] for x in pspace) for ray in D),
                     number_type='fraction')
        mat.rep_type = RepType.GENERATOR
        lin, red = mat.canonicalize()
        for i in red:
            self.discard(D[i])

    def set_lower_pr(self, data, val):
        """Set the lower probability/prevision (expectation) of an event/gamble

          :arg data: the gamble for which a probability/prevision value is given
          :type data: arguments accepted by the :class:`~murasyp.gambles.Gamble`
            constructor
          :arg val: the probability/prevision value
          :type val: a representation of :class:`~numbers.Real`

        The nontrivial diray corresponing to the prevision specification is
        calculated and added to the set of desirable gambles.

        >>> D = DesirSet()
        >>> D.set_lower_pr(Gamble({'a', 'b'}) | {'a', 'b', 'c'}, .4)
        >>> D
        DesirSet(set([DiRay({'a': 1, 'c': '-2/3', 'b': 1}, {'a': 1, 'c': 1, 'b': 1})]))

        .. note::

          The domain of the input gamble determines the conditioning event.

        """
        gamble = Gamble(data)
        self.add(DiRay(gamble - _make_rational(val), gamble.domain()))

    def set_upper_pr(self, data, val):
        """Set the upper probability/prevision (expectation) of an event/gamble

          :arg data: the gamble for which a probability/prevision value is given
          :type data: arguments accepted by the :class:`~murasyp.gambles.Gamble`
            constructor
          :arg val: the probability/prevision value
          :type val: a representation of :class:`~numbers.Real`

        The nontrivial diray corresponing to the prevision specification is
        calculated and added to the set of desirable gambles.

        >>> D = DesirSet()
        >>> D.set_upper_pr(Gamble({'a', 'b'}) | {'a', 'b', 'c'}, .4)
        >>> D
        DesirSet(set([DiRay({'a': -1, 'c': '2/3', 'b': -1}, {'a': 1, 'c': 1, 'b': 1})]))

        .. note::

          The domain of the input gamble determines the conditioning event.

        """
        gamble = Gamble(data)
        self.add(DiRay(_make_rational(val) - gamble, gamble.domain()))

    def set_pr(self, data, val):
        """Set the probability/prevision (expectation) of an event/gamble

          :arg data: the gamble for which a probability/prevision value is given
          :type data: arguments accepted by the :class:`~murasyp.gambles.Gamble`
            constructor
          :arg val: the probability/prevision value
          :type val: a representation of :class:`~numbers.Real`

        This is identical to setting the lower and upper prevision to the same
        value.

        >>> D = DesirSet()
        >>> D.set_pr(Gamble({'a', 'b'}) | {'a', 'b', 'c'}, .4)
        >>> D
        DesirSet(set([DiRay({'a': -1, 'c': '2/3', 'b': -1}, {'a': 1, 'c': 1, 'b': 1}), DiRay({'a': 1, 'c': '-2/3', 'b': 1}, {'a': 1, 'c': 1, 'b': 1})]))

        .. note::

          The domain of the input gamble determines the conditioning event.

        """
        self.set_lower_pr(data, val)
        self.set_upper_pr(data, val)

    def asl(self):
        """Check whether the set of desirable gambles avoids sure loss

          :rtype: :class:`bool`

        We solve a linear programming feasibility problem:
        If we can find a vector
        :math:`\lambda\in(\mathbb{R}_{\geq0})^{\mathcal{D}}`
        such that :math:`\sum_{g\in\mathcal{D}}\lambda_g\cdot g\leq-1`,
        then the set of desirable gambles :math:`\mathcal{D}` incurs sure loss,
        otherwise it avoids sure loss.

        >>> D = DesirSet(set('abc'))
        >>> D.add({'a': -1, 'b': -1, 'c': 1})
        >>> D.add({'a': 1, 'b': -1, 'c': -1})
        >>> D.asl()
        True
        >>> D.add({'a': -1, 'b': 1, 'c': -1})
        >>> D.asl()
        False

        """
        pspace = list(self.pspace())
        D = list(self)
        mat = Matrix(list([0] + [int(oray == ray) for oray in D] for ray in D) +
                     list([-1] + [-ray[x] for ray in D] for x in pspace),
                     number_type='fraction')
        mat.obj_type = LPObjType.MIN
        lp = LinProg(mat)
        lp.solve()
        return lp.status != LPStatusType.OPTIMAL

    def apl(self):
        """Check whether the set of desirable gambles avoids partial loss

          :rtype: :class:`bool`

        We have to solve a feasibility problem:
        Let :math:`\Omega` denote the possibility space, :math:`I_\omega` the
        ray corresponding to the :math:`\omega`-axis, and :math:`g'` the second
        tier part of :math:`g`.
        If there is a vector :math:`(\lambda,\\tau)
        \in(\mathbb{R}_{\geq0})^{\mathcal{D}\\times\Omega}` such that
        :math:`\sum_{\omega\in\Omega}\\tau_\omega\geq1`,
        :math:`\sum_{g\in\mathcal{D}}\lambda_g\cdot g
        \leq-\sum_{\omega\in\Omega}\\tau_\omega\cdot I_{\omega}`, and
        :math:`\sum_{g\in\mathcal{D}}\lambda_g\cdot g'(\omega)\leq0` for
        :math:`\omega` such that :math:`\\tau_\omega=0`, then the set of
        desirable gambles :math:`\mathcal{D}` incurs partial loss.

        This problem can be solved by solving an iteration of *linear
        programming* optimization problems (cf. [WPV2004]_, Algorithm 2):
        Assume that no partial loss is possible with nonzero values on a
        subset :math:`A_i` of :math:`\Omega`.
        We therefore check whether partial loss is possible with strictly
        negative values on its complement, or whether we need to focus on a
        smaller set :math:`A_{i+1}`.
        To do this, we try to find the vector :math:`(\lambda,\\tau)
        \in(\mathbb{R}_{\geq0})^{\mathcal{D}}\\times[0,1]^{\Omega\setminus A_i}`
        that maximizes
        :math:`\sum_{\omega\in\Omega\setminus A_i}\\tau_\omega` subject to
        :math:`\sum_{g\in\mathcal{D}}\lambda_g\cdot g \leq
        -\sum_{\omega\in\Omega\setminus A_i}\\tau_\omega\cdot I_{\omega}` and
        :math:`\sum_{g\in\mathcal{D}}\lambda_g\cdot g'(\omega)\leq0` for all
        :math:`\omega` in :math:`A_i`.
        In case :math:`\\tau=1`, then :math:`\mathcal{D}` incurs partial loss,
        otherwise we set
        :math:`A_{i+1}=A_i\cup\{\omega\in\Omega\setminus A_i: \\tau_\omega=0\}`.
        In case :math:`A_{i+1}=\Omega`, then :math:`\mathcal{D}` avoids
        partial loss, otherwise, we go to the next linear program in the
        iteration.

        **TODO**
        (Current implementation does not belong to this explanation!)

        >>> D = DesirSet(set('abc'))
        >>> D.add({'a': -1, 'b': -1, 'c': 1})
        >>> D.apl()
        True
        >>> D.add({'a': -1, 'b': 1, 'c': -1})
        >>> D.apl()
        False

        .. warning::

          Does not take the second tier ray of constituent dirays into account,
          as it should. So it may give an incorrect answer.

        """
        pspace = list(self.pspace())
        D = list(self)
        E = list(DesirSet(self.pspace()))
        mat = Matrix(list([0] + [int(oray == ray) for oray in D]
                              + len(E) * [0] for ray in D) +
                     list([0] + len(D) * [0]
                              + [int(oray == ray) for oray in E] for ray in E) +
                     list([0] + [-ray[x] for ray in D + E] for x in pspace) +
                     list([[-1] + len(D) * [0] + len(E) * [1]]),
                     number_type='fraction')
        mat.obj_type = LPObjType.MIN
        lp = LinProg(mat)
        lp.solve()
        return lp.status != LPStatusType.OPTIMAL

    def __mul__(self, other):
        """Lower expectation of a gamble"""
        if not isinstance(other, Gamble):
            raise TypeError(str(other) + " is not a gamble")
        dom = other.domain()
        pspace = list(self.pspace())
        D = list(self)
        mat = Matrix(list([0, 0] + [int(oray == ray) for oray in D]
                          for ray in D) +
                     list([other[x], -int(x in dom)] + [-ray[x] for ray in D]
                          for x in pspace),
                      number_type='fraction')
        mat.obj_type = LPObjType.MAX
        mat.obj_func = tuple([0, 1] + len(D) * [0])
        lp = LinProg(mat)
        lp.solve()
        if lp.status == LPStatusType.OPTIMAL:
            return lp.obj_value
        elif lp.status == LPStatusType.UNDECIDED:
            status = "undecided"
        elif lp.status == LPStatusType.INCONSISTENT:
            status = "inconsistent"
        elif lp.status == LPStatusType.UNBOUNDED:
            status = "unbounded"
        else:
            status = "of unknown status"
        raise ValueError("The linear program is " + str(status) + '.')

    def __pow__(self, other):
        """Upper expectation of a gamble"""
        return - self.__mul__(- other)

    def get_credal(self):
        """Generate the corresponding (closed) credal set

          :returns: the credal set that corresponds as an uncertainty model
          :rtype: :class:`~murasyp.credalsets.CredalSet`

        >>> D = DesirSet(set('abc'))
        >>> D.set_lower_pr({'a': 1, 'b': 0, 'c': 1}, .5)
        >>> D.get_credal()
        CredalSet(set([PMFunc({'a': '1/2', 'b': '1/2'}), PMFunc({'c': '1/2', 'b': '1/2'}), ...

        .. warning::

          We can only express closed credal sets currently.
          So therefore we currently do not take the second tier ray of
          constituent dirays into account.

        """
        pspace = list(self.pspace())
        D = list(self)
        mat = Matrix(list([0] + list(ray[x] for x in pspace) for ray in D),
                     number_type='fraction')
        mat.rep_type = RepType.INEQUALITY
        poly = Polyhedron(mat)
        ext = poly.get_generators()
        return CredalSet(set([PMFunc({pspace[j-1]: ext[i][j]
                                     for j in range(1, ext.col_size)})
                              for i in range(0, ext.row_size)] +
                             [PMFunc({pspace[j-1]: -ext[i][j]
                                     for j in range(1, ext.col_size)})
                              for i in ext.lin_set]))

from murasyp.credalsets import CredalSet # avoid circular-dependency
