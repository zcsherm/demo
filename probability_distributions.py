import discrete_models
from utilities import *
from math import exp, pi
from sympy import integrate, symbols, oo
from sympy.solvers import solveset

class Distribution:

    # Models a binomial distribution of n binary bernoulli trials with p chance of success
    def __init__(self):
        pass

    def get_standard_attributes(self):
        # allow for calling on mu or expected
        self._mu = self._expected
        self._standard_deviation = self._variance ** .5



# map string values to the classses for each distro
