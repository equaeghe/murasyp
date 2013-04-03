__version__ = '(git)'
__release__ = __version__

from fractions import Fraction

def _make_rational(value):
    """Make a Fraction of acceptable input"""
    if type(value) == float:
        value = str(value) # treat floats as decimal numbers
    try:
        return Fraction(value)
    except ValueError:
        print(repr(value) + " is not a Rational number")
