__version__ = '0.1'
__release__ = __version__

from fractions import Fraction

def _make_rational(value):
    try:
        return Fraction(str(value))
    except:
        print(repr(value) + " is not a Rational number")
