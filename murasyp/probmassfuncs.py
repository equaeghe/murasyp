from murasyp.massassignments import MassAssignment

class ProbMassFunc(MassAssignment):
    """Probability mass functions are immutable, hashable rational-valued
    functions with values that are nonnegative and sum to one.

      :param: a mapping (such as a :class:`dict`) to Rational values,
          i.e., :class:`~fractions.Fraction`. The fractions
          may be specified by giving an :class:`int`, a :class:`float` or in
          their :class:`str`-representation.
          The sum of the values must be nonzero.
      :type: :class:`~collections.Mapping`

    This class derives from :class:`~murasyp.massassignments.MassAssignment`,
    so its methods apply here as well. What has changed:

    * its values have to be positive.

    >>> p = ProbMassFunc({'a': .03, 'b': .07, 'c': .9})
    >>> p
    ProbMassFunc({'a': Fraction(3, 100), 'c': Fraction(9, 10), 'b': Fraction(7, 100)})
    >>> p | Event('ab')
    ProbMassFunc({'a': Fraction(3, 10), 'b': Fraction(7, 10)})
    >>> ProbMassFunc({'a': -1, 'b': 2})
    Traceback (most recent call last):
    ...
    ValueError: probability mass functions must have nonnegative values

    """

    def __init__(self, data):
        """Create a probability mass function"""
        MassAssignment.__init__(self, data)
        if not self.is_pmf():
            raise ValueError("probability mass functions "
                             + "must have nonnegative values")
