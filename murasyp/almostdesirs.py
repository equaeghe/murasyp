from collections import Set, MutableSet, Mapping
from cdd import Matrix, RepType
from murasyp.gambles import Gamble, Ray

class ADesirSet(MutableSet):
    """A mutable set of rays

      :param: a :class:`~collections.Set` of :class:`~collections.Mapping`,
          each of which can be normalized to a :class:`~murasyp.gambles.Ray`,
          i.e., it must be nonconstant.
      :type: :class:`~collections.Set`

    Features:

    * There is an alternate constructor. If `data` is a
      :class:`~collections.Set` without :class:`~collections.Mapping`-members
      then a relative set of almost desirable gambles is generated.

      >>> ADesirSet(set('abc'))
      ADesirSet(set([Ray({'a': 1}), Ray({'b': 1}), Ray({'c': 1})]))

    """
    def __init__(self, data=set([])):
        """Create a set of almost desirable gambles"""
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

    def add(self, mapping):
        """Add a ray to the set of almost desirable gambles

          :param: a mapping that can be normalized to a
              :class:`~murasyp.gambles.Ray`, i.e., it must be nonconstant.
          :type: :class:`~collections.Mapping`

        >>> D = ADesirSet()
        >>> D
        ADesirSet(set([]))
        >>> D.add({'a': -.06, 'b': .14, 'c': 1.8, 'd': 0})
        >>> D
        ADesirSet(set([Ray({'a': '-1/30', 'c': 1, 'b': '7/90'})]))

        """
        self._set.add(Ray(mapping))

    def discard(self, mapping):
        """Remove a ray from the credal set

          :param: a mapping that can be normalized to a
              :class:`~murasyp.gambles.Ray`, i.e., it must be nonconstant.
          :type: :class:`~collections.Mapping`

        >>> D = ADesirSet({'a','b'})
        >>> D
        ADesirSet(set([Ray({'a': 1}), Ray({'b': 1})]))
        >>> D.discard(Ray({'a'}))
        >>> D
        ADesirSet(set([Ray({'b': 1})]))

        """
        self._set.discard(Ray(mapping))

    __len__ = lambda self: self._set.__len__()
    __iter__ = lambda self: self._set.__iter__()
    __contains__ = lambda self: self._set.__contains__()
    __repr__ = lambda self: type(self).__name__ + '(' + repr(self._set) + ')'

    def pspace(self):
        """The possibility space of the set of desirable gambles

        >>> r = Ray({'a': .03, 'b': -.07})
        >>> s = Ray({'a': .07, 'c': -.03})
        >>> K = ADesirSet({r, s})
        >>> K.pspace()
        frozenset(['a', 'c', 'b'])

        """
        return frozenset.union(*(ray.domain() for ray in self))

    def discard_redundant(self):
        """Remove redundant elements from the set of desirable gambles

        Redundant elements are those that are not extreme rays of set of
        desirable gambles's convex conical hull.

        >>> D = ADesirSet(set('abc'))
        >>> D.add({'a': 1, 'b': 1, 'c': 1})
        >>> D
        ADesirSet(set([Ray({'a': 1, 'c': 1, 'b': 1}), ...]))
        >>> D.discard_redundant()
        >>> D
        ADesirSet(set([Ray({'a': 1}), Ray({'b': 1}), Ray({'c': 1})]))

        """
        pspace = list(self.pspace())
        D = list(self)
        mat = Matrix(list([0] + list(ray[x] for x in pspace) for ray in D),
                     number_type='fraction')
        mat.rep_type = RepType.GENERATOR
        lin, red = mat.canonicalize()
        for i in red:
            self.discard(D[i])
