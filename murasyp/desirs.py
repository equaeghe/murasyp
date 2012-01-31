from collections import Set, MutableSet, Mapping
from cdd import Matrix, LPObjType, LinProg, LPStatusType, RepType, Polyhedron
from murasyp import _make_rational
from murasyp.gambles import Gamble, Ray
from murasyp.massfuncs import PMFunc

class DesirSet(MutableSet):
    """A mutable set of rays

      :type data: a :class:`~collections.Set` of :class:`~collections.Mapping`,
          each of which can be normalized to a :class:`~murasyp.gambles.Ray`,
          i.e., it must be nonconstant.

    Features:

    * There is an alternate constructor. If `data` is a
      :class:`~collections.Set` without :class:`~collections.Mapping`-members,
      then a relative set of desirable gambles is generated.

      >>> DesirSet(set('abc'))
      DesirSet(set([Ray({'a': 1}), Ray({'b': 1}), Ray({'c': 1})]))

    * Lower and upper (conditional) expectations can be calculated, using the
      ``*`` and ``**`` operators, respectively.

      >>> D = DesirSet(set([Ray({'a': -1, 'c': '7/90'}),
      ...                   Ray({'a': 1, 'c': '-1/30'}),
      ...                   Ray({'a': -1, 'c': '1/9', 'b': -1}),
      ...                   Ray({'a': 1, 'c': '-1/9', 'b': 1})]))
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

        These operations are not dependable when dealing with a set of
        almost desirable gambles.

    """
    def __init__(self, data=set([])):
        """Create a set of desirable gambles"""
        if isinstance(data, Set):
            are_mappings = [isinstance(elem, Mapping) for elem in data]
            if all(are_mappings):
                self._set = set(Ray(mapping) for mapping in data)
            elif not any(are_mappings):
                self._set = set(Ray({x}) for x in data) # vacuous
            else:
                raise TypeError("either all or none of the elements of the "
                                + "specified Set " + str(data) + "must be "
                                + "Mappings")
        else:
            raise TypeError("specify a Set instead of a "
                            + type(data).__name__)

    def add(self, data):
        """Add a ray to the set of desirable gambles

          :type data: arguments accepted by the :class:`~murasyp.gambles.Ray`
            constructor

        >>> D = DesirSet()
        >>> D
        DesirSet(set([]))
        >>> D.add({'a': -.06, 'b': .14, 'c': 1.8, 'd': 0})
        >>> D
        DesirSet(set([Ray({'a': '-1/30', 'c': 1, 'b': '7/90'})]))

        """
        self._set.add(Ray(data))

    def discard(self, data):
        """Remove a ray from the credal set

          :type data: arguments accepted by the :class:`~murasyp.gambles.Ray`
            constructor

        >>> D = DesirSet({'a','b'})
        >>> D
        DesirSet(set([Ray({'a': 1}), Ray({'b': 1})]))
        >>> D.discard(Ray({'a'}))
        >>> D
        DesirSet(set([Ray({'b': 1})]))

        """
        self._set.discard(Ray(data))

    __len__ = lambda self: self._set.__len__()
    __iter__ = lambda self: self._set.__iter__()
    __contains__ = lambda self: self._set.__contains__()
    __repr__ = lambda self: type(self).__name__ + '(' + repr(self._set) + ')'

    def pspace(self):
        """The possibility space of the set of desirable gambles

          :returns: the possibility space of the set of desirable gambles, i.e.,
            the union of the domains of the rays it contains
          :rtype: :class:`frozenset`

        >>> r = Ray({'a': .03, 'b': -.07})
        >>> s = Ray({'a': .07, 'c': -.03})
        >>> D = DesirSet({r, s})
        >>> D.pspace()
        frozenset(['a', 'c', 'b'])

        """
        return frozenset.union(*(ray.domain() for ray in self))

    def discard_redundant(self):
        """Remove redundant elements from the set of desirable gambles

        Redundant elements are those that are not extreme rays of set of
        desirable gambles's convex conical hull.

        >>> D = DesirSet(set('abc'))
        >>> D.add({'a': 1, 'b': 1, 'c': 1})
        >>> D
        DesirSet(set([Ray({'a': 1, 'c': 1, 'b': 1}), ...]))
        >>> D.discard_redundant()
        >>> D
        DesirSet(set([Ray({'a': 1}), Ray({'b': 1}), Ray({'c': 1})]))

        """
        pspace = list(self.pspace())
        D = list(self)
        mat = Matrix(list([0] + list(ray[x] for x in pspace) for ray in D),
                     number_type='fraction')
        mat.rep_type = RepType.GENERATOR
        lin, red = mat.canonicalize()
        for i in red:
            self.discard(D[i])

    def set_lower_pr(self, data, val):
        """Set the lower probability/prevision (expectation) of an event/gamble

          :arg data: the gamble for which a probability/prevision value is given
          :type data: arguments accepted by the :class:`~murasyp.gambles.Ray`
            constructor
          :arg val: the probability/prevision value
          :type val: a representation of :class:`~numbers.Real`

        The marginal gamble corresponing to the prevision specification is
        calculated and added to the set of desirable gambles.

        >>> D = DesirSet()
        >>> D.set_lower_pr(Gamble({'a', 'b'}) | {'a', 'b', 'c'}, .4)
        >>> D
        DesirSet(set([Ray({'a': 1, 'c': '-2/3', 'b': 1})]))

        .. note::

          The domain of the input gamble determines the conditioning event.

        .. warning::

          The set of desirable gambles becomes a set of *almost* desirable
          gambles.

        """
        self.add(Gamble(data) - _make_rational(val))

    def set_upper_pr(self, data, val):
        """Set the upper probability/prevision (expectation) of an event/gamble

          :arg data: the gamble for which a probability/prevision value is given
          :type data: arguments accepted by the :class:`~murasyp.gambles.Ray`
            constructor
          :arg val: the probability/prevision value
          :type val: a representation of :class:`~numbers.Real`

        The marginal gamble corresponing to the prevision specification is
        calculated and added to the set of desirable gambles.

        >>> D = DesirSet()
        >>> D.set_upper_pr(Gamble({'a', 'b'}) | {'a', 'b', 'c'}, .4)
        >>> D
        DesirSet(set([Ray({'a': -1, 'c': '2/3', 'b': -1})]))

        .. note::

          The domain of the input gamble determines the conditioning event.

        .. warning::

          The set of desirable gambles becomes a set of *almost* desirable
          gambles.

        """
        self.add(_make_rational(val) - Gamble(data))

    def set_pr(self, data, val):
        """Set the probability/prevision (expectation) of an event/gamble

          :arg data: the gamble for which a probability/prevision value is given
          :type data: arguments accepted by the :class:`~murasyp.gambles.Ray`
            constructor
          :arg val: the probability/prevision value
          :type val: a representation of :class:`~numbers.Real`

        This is identical to setting the lower and upper prevision to the same
        value.

        >>> D = DesirSet()
        >>> D.set_pr(Gamble({'a', 'b'}) | {'a', 'b', 'c'}, .4)
        >>> D
        DesirSet(set([Ray({'a': -1, 'c': '2/3', 'b': -1}), Ray({'a': 1, 'c': '-2/3', 'b': 1})]))

        .. note::

          The domain of the input gamble determines the conditioning event.

        .. warning::

          The set of desirable gambles becomes a set of *almost* desirable
          gambles.

        """
        self.set_lower_pr(data, val)
        self.set_upper_pr(data, val)

    def asl(self):
        """Check whether the set of desirable gambles avoids sure loss

          :rtype: :class:`bool`

        We solve a feasibility (linear programming) problem: If we can find
        a vector :math:`\lambda\in(\mathbb{R}_{\geq0})^{\mathcal{D}}`
        such that :math:`\sum_{f\in\mathcal{D}}\lambda_f\cdot f\leq-1`,
        then the set of desirable gambles :math:`\mathcal{D}`
        incurs sure loss.

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

        We solve a feasibility (linear programming) problem:
        If we can find a vector :math:`(\lambda,\\tau)
        \in(\mathbb{R}_{\geq0})^{\mathcal{D}\\times\Omega}` such that
        :math:`\sum_{f\in\mathcal{D}}\lambda_f\cdot f
        \leq-\sum_{\omega\in\Omega}\\tau_\omega\cdot I_{\omega}`
        and :math:`\sum_{\omega\in\Omega}\\tau_\omega\geq1`,
        where :math:`I_\omega` is the ray corresponding to
        the :math:`\omega`-axis, then the set of desirable gambles
        :math:`\mathcal{D}` incurs partial loss.

        >>> D = DesirSet(set('abc'))
        >>> D.add({'a': -1, 'b': -1, 'c': 1})
        >>> D.apl()
        True
        >>> D.add({'a': -1, 'b': 1, 'c': -1})
        >>> D.apl()
        False

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
        pspace = self.pspace()
        #if not (dom <= pspace):
            #raise ValueError("The gamble's domain (conditioning event) " +
                             #"is not a subset of the possibility space")
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
        """Generate the equivalent credal set

          :returns: the credal set that is equivalent as an uncertainty model
          :rtype: :class:`~murasyp.credalsets.CredalSet`

        >>> D = DesirSet(set('abc'))
        >>> D.set_lower_pr({'a': 1, 'b': 0, 'c': 1}, .5)
        >>> D.get_credal()
        CredalSet(set([PMFunc({'a': '1/2', 'b': '1/2'}), PMFunc({'c': '1/2', 'b': '1/2'}), ...

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
