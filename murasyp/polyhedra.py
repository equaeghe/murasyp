from collections import MutableSet, Hashable
from murasyp.vectors import Vector

class Cone(Hashable, MutableSet):
    """A convex cone; the conical hull of a set of vectors"""

    def __init__(self, data={}, frozen=False, element_type=Vector):
        """Create a convex cone"""
        try:
            self._set = {self.element_type(arg).max_normed() for arg in data}
        self._frozen = frozen
        self._element_type = element_type

class Polytope(Hashable, MutableSet):
    """A convex polytope; the convex hull of a set of vectors"""