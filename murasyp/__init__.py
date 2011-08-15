__version__ = '0.1'
__release__ = __version__

from fractions import Fraction

def _make_rational(value):
    """Make a Fraction of acceptable input"""
    try:
        return Fraction(str(value)) # avoid float to Fraction by going to string
    except:
        print(repr(value) + " is not a Rational number")
