from murasyp.vectors import Polytope
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
