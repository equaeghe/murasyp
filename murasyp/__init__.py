from fractions import Fraction

__version__ = '(git)'
__release__ = __version__

def _make_rational(value):
    """Make a Fraction of acceptable input"""
    try:
        return Fraction(str(value))
    except ValueError(repr(value) + " is not a rational number"):
        raise
