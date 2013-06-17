from collections import Set, MutableSet
from murasyp import Freezable
from murasyp.vectors import Vector
from cdd import Matrix, RepType, LPObjType, LinProg, LPStatusType

class _VectorHull(Freezable, MutableSet):
    """A set of vectors"""

    def __init__(self, data={}, frozen=False,
                 primal_type=Vector, dual_type=Vector):
        self._primal_type = primal_type
        self._dual_type = dual_type
        self._set = {self._primal_type(arg, None) for arg in data}
        self._frozen = frozen

    __len__ = lambda self: len(self._set)
    __iter__ = lambda self: iter(self._set)

    def __contains__(self, vector):
        mat = Matrix(number_type='fraction')
        self._add_tableau(mat, vector)
        self._add_coefficient_constraints(mat)
        mat.rep_type = RepType.GENERATOR
        mat.obj_type = LPObjType.MAX # does not matter, feasibility problem
        mat.obj_func = (0,) + len(self) * (0,) # feasibility, so constant objective
        lp = LinProg(mat)
        lp.solve()
        return lp.status == LPStatusType.OPTIMAL

    def _add_tableau(self, mat, vector=Vector({})):
        ordered_self = list(self)
        mat.extend([[vector[arg]] + [-w[arg] for w in ordered_self]
                    for arg in self.domain()], linear=True)

    def _add_coefficient_constraints(self, mat):
        raise NotImplementedError

    __hash__ = Set._hash

    def __and__(self, other):
        raise NotImplementedError

    def __sub__(self, other):
        raise AttributeError

    def __xor__(self, other):
        raise AttributeError

    @Freezable.freeze_safe
    def add(self, elem):
        self._set.add(self._element_type(elem))

    @Freezable.freeze_safe
    def discard(self, elem):
        self._set.discard(self._element_type(elem))

    def domain(self):
        """The union of the domains of all vectors in the set"""
        return frozenset.union(*(vector.domain() for vector in self))


class Cone(_VectorSet):
    """A convex cone; the positive linear hull of a set of vectors"""

    def _add_coefficient_constraints(self, mat):
        indices = range(len(self))
        mat.extend([[0] + [int(i == j) for j in indices] for i in indices])


class Polytope(_VectorSet):
    """A convex polytope; the convex hull of a set of vectors"""

    def _add_coefficient_constraints(self, mat):
        indices = range(len(self))
        mat.extend([[0] + [int(i == j) for j in indices] for i in indices])
        mat.extend([[1] + [-1]], linear=True)
