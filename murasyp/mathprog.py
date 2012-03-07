from murasyp.vectors import Vector, Polytope
from cdd import Matrix, RepType, Polyhedron

def vf_enumeration(data=[]):
    """Perform vertex/facet enumeration

      :type `data`: an argument accepted by the
        :class:`~murasyp.vectors.Polytope` constructor.

    :returns: the vertex/facet enumeration of the polytope (assumed to be in
      facet/vertex-representation)
    :rtype: a :class:`~murasyp.vectors.Polytope`

    """
    vf_poly = Polytope(data)
    coordinates = list(vf_poly.domain())
    mat = Matrix(list([0] + [vector[x] for x in coordinates]
                      for vector in vf_poly),
                 number_type='fraction')
    mat.rep_type = RepType.INEQUALITY
    poly = Polyhedron(mat)
    ext = poly.get_generators()
    fv_poly = Polytope([{coordinates[j-1]: ext[i][j]
                         for j in range(1, ext.col_size)}
                        for i in range(0, ext.row_size)] +
                       [{coordinates[j-1]: -ext[i][j]
                         for j in range(1, ext.col_size)}
                        for i in ext.lin_set])
    return fv_poly

def feasible(data, mapping):
    """Check feasibility using the CONEstrip algorithm"""
    D = set(Polytope(A) for A in data)
    h = Vector(mapping)
    D.add([-h])
    coordinates = list(frozenset.union(*(A.domain() for A in D)))
    E = [[vector for vector in A] for A in D]
    while (E != []):
        k = len(E)
        L = [len(A) for A in E]
        l = sum(L)
        mat = Matrix([[0] + [v[x] for v in A for A in E] + k * [0]
                      for x in coordinates] + # cone-constraints
                     [[0] + [int(w == v) for w in A for A in E] + k * [0]
                      for v in A for A in E] + # μ >= 0
                     [[-1] + [int(w == -h) for w in A for A in E] + k * [0]] +
                     [[0] + l * [0] + [int(B == A) for B in E]
                      for A in E] + # τ >= 0
                     [[1] + l * [0] + [-int(B == A) for B in E]
                      for A in E] + # τ <= -1
                     [[0] + l * [0] + k * [1]] + # (sum of τ_A) >= 0
                     [[0] + [int(w == v) for w in A for A in E]
                          + [-int(B == A) for B in E]
                      for v in A for A in E], # τ_A <= μ_A
                     number_type='fraction')
        mat.obj_type = LPObjType.MAX
        mat.obj_func = tuple([0] + l * [0] + k * [1])
        lp = LinProg(mat)
        lp.solve()
        if lp.status == LPStatusType.OPTIMAL:
            sol = LinProg.primal_solution
            F = [E[n] for n in range(0, k) if sol[1 + l:][n] == 1]
            if all(all(sol[sum(L[0:n]):sum(L[0:n]) + L[n]][m] == 0
                       for m in range(0, L[n]))
                   for n in range(0, k) if sol[1 + l:][n] == 0):
                return F
            else:
                E = F
                continue
        else:
            return []
    else:
        return []
