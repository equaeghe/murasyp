# coding: utf-8

from collections import Set, MutableSet, Mapping
from cdd import Matrix, LPObjType, LinProg, LPStatusType, RepType, Polyhedron
from murasyp import _make_rational
from murasyp.gambles import Gamble, Ray, Cone
from murasyp.massfuncs import PMFunc

class DesirSet(MutableSet):
    """A mutable set of cones

      :type data: a :class:`~collections.Set` of arguments accepted by the
        :class:`~murasyp.gambles.Cone` constructor.

    Features:

    * There is an alternative constructor that accepts possibility spaces:

      >>> DesirSet(set('abc'))
      DesirSet(set([Cone(frozenset([Ray({'b': 1})])), Cone(frozenset([Ray({'c': 1})])), Cone(frozenset([Ray({'a': 1})]))]))

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

      .. admonition:: Algorithm

          We have to solve an optimization problem:
          ***todo***

      .. warning::

          Currently returns possibly incorrect answer.

    """
    def __init__(self, data=set()):
        """Create a set of desirable gambles"""
        if isinstance(data, Set):
            try:
                self._set = {Cone(element) for element in data}
            except:
                self._set = {Cone({element}) for element in data}
        else:
            raise TypeError("specify a Set instead of a " + type(data).__name__)

    def add(self, data):
        """Add a cone to the set of desirable gambles

          :type data: arguments accepted by the :class:`~murasyp.gambles.Cone`
            constructor

        >>> D = DesirSet()
        >>> D
        DesirSet(set([]))
        >>> D.add({Gamble({'a': -.06, 'b': .14, 'c': 1.8, 'd': 0})})
        >>> D
        DesirSet(set([Cone(frozenset([Ray({'a': '-1/30', 'c': 1, 'b': '7/90'})]))]))

        """
        self._set.add(Cone(data))

    def discard(self, data):
        """Remove a cone from the set of desirable gambles

          :type data: arguments accepted by the :class:`~murasyp.gambles.Cone`
            constructor

        >>> D = DesirSet({'a','b'})
        >>> D
        DesirSet(set([Cone(frozenset([Ray({'b': 1})])), Cone(frozenset([Ray({'a': 1})]))]))
        >>> D.discard({Ray({'a'})})
        >>> D
        DesirSet(set([Cone(frozenset([Ray({'b': 1})]))]))

        """
        self._set.discard(frozenset(Ray(element) for element in data))

    __len__ = lambda self: self._set.__len__()
    __iter__ = lambda self: self._set.__iter__()
    __contains__ = lambda self: self._set.__contains__()
    __repr__ = lambda self: type(self).__name__ + '(' + repr(self._set) + ')'

    def pspace(self):
        """The possibility space of the set of desirable gambles

          :returns: the possibility space of the set of desirable gambles, i.e.,
            the union of the domains of the cones it contains
          :rtype: :class:`frozenset`

        >>> D = DesirSet(set('abc'))
        >>> r = Ray({'c': .03, 'd': -.07})
        >>> s = Ray({'a': .07, 'e': -.03})
        >>> D .add({r, s})
        >>> D.pspace()
        frozenset(['a', 'c', 'b', 'e', 'd'])

        """
        return frozenset.union(*(cone.domain() for cone in self))

    def set_lower_pr(self, data, val):
        """Set the lower probability/prevision (expectation) of an event/gamble

          :arg data: the gamble for which a probability/prevision value is given
          :type data: arguments accepted by the :class:`~murasyp.gambles.Gamble`
            constructor
          :arg val: the probability/prevision value
          :type val: a representation of :class:`~numbers.Real`

        The nontrivial cone corresponing to the prevision specification is
        calculated and added to the set of desirable gambles.

        >>> D = DesirSet()
        >>> D.set_lower_pr(Gamble({'a', 'b'}) | {'a', 'b', 'c'}, .4)
        >>> D
        DesirSet(set([Cone(frozenset([Ray({'a': 1, 'c': 1, 'b': 1}), Ray({'a': 1, 'c': '-2/3', 'b': 1})]))]))

        .. note::

          The domain of the input gamble determines the conditioning event.

        """
        gamble = Gamble(data)
        self.add({gamble - _make_rational(val), Ray(gamble.domain())})

    def set_upper_pr(self, data, val):
        """Set the upper probability/prevision (expectation) of an event/gamble

          :arg data: the gamble for which a probability/prevision value is given
          :type data: arguments accepted by the :class:`~murasyp.gambles.Gamble`
            constructor
          :arg val: the probability/prevision value
          :type val: a representation of :class:`~numbers.Real`

        The nontrivial cone corresponing to the prevision specification is
        calculated and added to the set of desirable gambles.

        >>> D = DesirSet()
        >>> D.set_upper_pr(Gamble({'a', 'b'}) | {'a', 'b', 'c'}, .4)
        >>> D
        DesirSet(set([Cone(frozenset([Ray({'a': 1, 'c': 1, 'b': 1}), Ray({'a': -1, 'c': '2/3', 'b': -1})]))]))

        .. note::

          The domain of the input gamble determines the conditioning event.

        """
        self.set_lower_pr(-Gamble(data), -val)

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
        DesirSet(set([Cone(frozenset([Ray({'a': 1, 'c': 1, 'b': 1}), Ray({'a': 1, 'c': '-2/3', 'b': 1})])), Cone(frozenset([Ray({'a': 1, 'c': 1, 'b': 1}), Ray({'a': -1, 'c': '2/3', 'b': -1})]))]))

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

        >>> D = DesirSet(set('abc'))
        >>> D.add({'a': -1, 'b': -1, 'c': 1})
        >>> D.add({'a': 1, 'b': -1, 'c': -1})
        >>> D.asl()
        True
        >>> D.add({'a': -1, 'b': 1, 'c': -1})
        >>> D.asl()
        False

        .. admonition:: Algorithm

            We have to solve a linear programming feasibility problem:
            If we can find a vector
            :math:`\lambda\in(\mathbb{R}_{\geq0})^{\mathcal{D}}`
            such that :math:`\sum_{g\in\mathcal{D}}\lambda_g\cdot g\leq-1`,
            then the set of desirable gambles :math:`\mathcal{D}` incurs sure loss,
            otherwise it avoids sure loss.

        .. note::

            The second-tier ray of the constituent dirays is ignored.

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

        A set of desirable gambles does not avoid partial loss if and only if
        some nonnegative linear combination of desirable gambles is everywhere
        nonpositive and somewhere negative.

        >>> D = DesirSet(set('abc'))
        >>> D.add({'a': -1, 'b': -1, 'c': 1})
        >>> D.apl()
        True
        >>> D.add({'a': -1, 'b': 1, 'c': -1})
        >>> D.apl()
        False

        We can deal correctly with non-closed sets of desirable gambles, i.e.,
        containing nontrivial dirays:

        >>> D = DesirSet(set('abc'))
        >>> D.set_upper_pr(Gamble({'a', 'b'}) | {'a', 'b', 'c'}, 0)
        >>> D
        DesirSet(set([DiRay({'a': -1, 'b': -1}, {'a': 1, 'c': 1, 'b': 1}), ...]))
        >>> D.apl()
        True

        .. admonition:: Algorithm

            We have to solve a feasibility problem:
            Let :math:`\Omega` denote the possibility space, :math:`I_\omega` the
            ray corresponding to the :math:`\omega`-axis, and :math:`g'` the second
            tier part of :math:`g`.
            If there is a vector :math:`(\lambda,\\tau)
            \in(\mathbb{R}_{\geq0})^{\mathcal{D}\\times\Omega}` such that
            :math:`\sum_{\omega\in\Omega}\\tau_\omega\geq1`,
            :math:`\sum_{g\in\mathcal{D}}\lambda_g\cdot g
            \leq-\sum_{\omega\in\Omega}\\tau_\omega\cdot I_{\omega}`, and
            :math:`\lambda_g\cdot g'(\omega)\leq0` for
            :math:`\omega` such that :math:`\\tau_\omega=0` and for all
            :math:`g` in :math:`\mathcal{D}`, then the set of desirable gambles
            :math:`\mathcal{D}` incurs partial loss.

            This problem can be solved by solving an iteration of *linear
            programming* optimization problems (cf. [WPV2004]_, Algorithm 2):
            Assume that no partial loss is possible with nonzero values outside a
            subset :math:`A_i` of :math:`\Omega`.
            We therefore check whether partial loss is possible with strictly
            negative values on :math:`A_i`, or whether we need to focus on a
            smaller set :math:`A_{i+1}`.
            To do this, we try to find the vector :math:`(\lambda,\\tau)
            \in(\mathbb{R}_{\geq0})^{\mathcal{D}}\\times[0,1]^{A_i}`
            that maximizes :math:`\sum_{\omega\in A_i}\\tau_\omega` subject to
            :math:`\sum_{g\in\mathcal{D}}\lambda_g\cdot g \leq
            -\sum_{\omega\in A_i}\\tau_\omega\cdot I_{\omega}` and
            :math:`\lambda_g\cdot g'|_{\Omega\setminus A_i}\leq0` for all
            :math:`g` in :math:`\mathcal{D}`.
            In case :math:`\\tau=1`, then :math:`\mathcal{D}` incurs partial
            loss, otherwise we set
            :math:`A_{i+1}=\{\omega\in A_i: \\tau_\omega=1\}`.
            In case :math:`A_{i+1}=\emptyset`, then :math:`\mathcal{D}` avoids
            partial loss, otherwise, we go to the next linear program in the
            iteration.

        """
        pspace = self.pspace()
        A = pspace
        while len(A) > 0:
            D = list(self)
            I = list(DesirSet(A))
            mat = Matrix([[0] + [int(oray == ray) for oray in D] + len(I) * [0]
                          for ray in D] # λ >= 0
                       + [[0] + len(D) * [0] + [int(oray == ray) for oray in I]
                          for ray in I] # τ >= 0
                       + [[1] + len(D) * [0] + [-int(oray == ray) for oray in I]
                          for ray in I] # τ <= 1
                       + [[0] + [-ray[x] for ray in D + I]
                          for x in pspace] # <λ,id>_D <= -<τ,id>_I
                       + [[0] + [-ray.dir[x]*int(oray == ray) for oray in D]
                              + len(I) * [0] # λ_g⋅g'(ω) <= 0
                          for x in pspace - A for ray in D], # for ω s.t. τ_ω=0
                         number_type='fraction')
            mat.obj_type = LPObjType.MAX
            mat.obj_func = tuple([0] + len(D) * [0] + len(I) * [1])
            lp = LinProg(mat)
            lp.solve()
            if lp.status != LPStatusType.OPTIMAL:
                raise ValueError("No solution found for linear program. " +
                                 "pycddlib returned status code " +
                                 "'" + lp.status + "'.")
            else:
                tau = lp.primal_solution[-len(I):]
                if not any(tau):
                    return True
                elif all(tau):
                    return False
                else:
                    A = sum(Gamble(I[k]) for k in range(0, len(tau))
                                         if tau[k] == 1).support()

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
