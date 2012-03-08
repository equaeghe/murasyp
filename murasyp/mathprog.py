# coding: utf-8

from murasyp.vectors import Vector, Polytope
from cdd import Matrix, RepType, Polyhedron, LPObjType, LinProg, LPStatusType

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

def feasible(data, mapping=None):
    """Check feasibility using the CONEstrip algorithm"""
    D = set(Polytope(A) for A in data)
    if (mapping == None) or all(mapping[x] != 0 for x in h):
        h = None
    else:
        h = Vector(mapping)
        D.add([-h])
    coordinates = list(frozenset.union(*(A.domain() for A in D)))
    E = [[vector for vector in A] for A in D]
    #print(E)
    while (E != []):
        k = len(E)
        L = [len(A) for A in E]
        l = sum(L)
        mat = Matrix([[0] + l * [0] + k * [0]], number_type='fraction')
        mat.extend([[0] + [v[x] for A in E for v in A  ] + k * [0]
                    for x in coordinates], linear=True) # cone-constraints
        mat.extend([[0] + [int(w == v) for B in E for w in B] + k * [0]
                    for A in E for v in A]) # mu >= 0
        mat.extend([[1] + l * [0] + [-int(B == A) for B in E]
                    for A in E]) # tau <= 1
        mat.extend([[0] + l * [0] + [int(B == A) for B in E]
                    for A in E]) # tau >= 0
        mat.extend([[-1] + l * [0] + k * [1]]) # (sum of tau_A) >= 1
        mat.extend([[0] + [int(w == v) for B in E for w in B]
                        + [-int(B == A) for B in E]
                    for A in E for v in A]) # tau_A <= mu_A for all A
        if h != None: # mu_{-h} >= 1
            mat.extend([[-1] + [int(w == -h) for A in E for w in A] + k * [0]])
        mat.obj_type = LPObjType.MAX
        mat.obj_func = tuple([0] + l * [0] + k * [1]) # (constant, mu, tau)
        #print(mat)
        lp = LinProg(mat)
        lp.solve()
        if lp.status == LPStatusType.OPTIMAL:
            sol = lp.primal_solution # (constant, mu, tau)
            tau = sol[l:]
            #print(tau)
            mu = [sol[sum(L[0:n]):sum(L[0:n]) + L[n]] for n in range(0, k)]
            #print(mu)
            E = [E[n] for n in range(0, k) if tau[n] == 1]
            #print(E)
            if all(all(mu[n][m] == 0 for m in range(0, L[n]))
                   for n in range(0, k) if tau[n] == 0):
                E = {Polytope(A) for A in E}
                #print(E)
                if h != None:
                    E = E - {Polytope([-h])}
                    #print(E)
                return E
            else:
                continue
        else:
            return set()
    else:
        return set()
