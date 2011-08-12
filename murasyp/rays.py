from murasyp.gambles import Gamble

class Ray(Gamble):
    """Rays are immutable, hashable rational-valued with max-norm one.

      :param: a mapping (such as a :class:`dict`) to Rational values,
          i.e., :class:`~fractions.Fraction`. The fractions
          may be specified by giving an :class:`int`, a :class:`float` or in
          their :class:`str`-representation.
          The sum of the values must be nonzero.
      :type: :class:`~collections.Mapping`

    This class derives from :class:`~murasyp.gambles.Gamble`, so its methods
    apply here as well. What has changed:

    * its max-norm has to be one;
    * the support becomes the domain.

    """

    def __init__(self, data):
        """Create a ray"""
        f = Gamble(data).normalized()
        Gamble.__init__(self, f | f.support())
