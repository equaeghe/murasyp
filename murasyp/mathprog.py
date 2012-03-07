from cdd import Matrix, RepType, Polyhedron

def enumeration(data=[]):
    """Perform vertex/facet enumeration

      :type `data`: a non-:class:`~collections.Mapping`
        :class:`~collections.Iterable` :class:`~collections.Container` of arguments accepted by the  :class:`~murasyp.vectors.Vector`
        constructor.

      :returns: the vertex/facet enumeration of the polytope
        facet/vertex-represented by the given vectors
      :rtype: a :class:`~list` of :class:`~murasyp.vectors.Vector`

    """
    raise NotImplementedError
