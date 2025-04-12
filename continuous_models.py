from probability_distributions import *

class Function_probability:
    # Represents when the probability is a function
    def __init__(self, function_string=None, lower_bound=0, upper_bound=oo):
        if function_string is None:
            self.get_function()
        else:
            self._function_string = function_string
        self.read_function()
        self._lower_bound = lower_bound
        self._upper_bound = upper_bound
        self.get_cdf_function()
        self._expected_value = self.get_expected_value()
        self._variance = self.get_variance()
        # self.get_standard_attributes()

    def get_function(self, function_string=None):
        # Get the function written as a string, e = e, p = pi, xyz can be variables
        if function_string is None:
            self._function_string = input("Please enter a function using 0-9,()+-/*^,e,p,xyz: ").strip()
            while not self.validate_function():
                self._function_string = input(
                    "The function you entered had an invalid character, please enter a function using 0-9,()+-/*^,e,p,xyz: ").strip()
        else:
            self._function_string = function_string

    def get_cdf_function(self):
        # Get the indefinite integral
        # Currently, it only treats x as the variable of integration
        x, y, z = symbols("x y z")
        integratable_string = ""
        integratable_string = self._function_string.replace("^", "**")
        integratable_string = integratable_string.replace('p', "pi")
        integratable_string = integratable_string.replace('e', "exp(1)")
        self._integratable_string = integratable_string
        self._indef_integral = integrate(integratable_string, x)

    def probability_mass_function(self, *args):
        # Integration
        # Potentially run a limit as it approaches the passed arg?
        pass

    def cumulative_density_function(self, lower_bound=None, upper_bound=None, *args, **kwargs):
        lower_bound = set_default_value(lower_bound, self._lower_bound)
        upper_bound = set_default_value(upper_bound, self._upper_bound)
        x, y, z = symbols("x y z")
        upper_integral = self._indef_integral.subs(x, upper_bound)
        lower_integral = self._indef_integral.subs(x, lower_bound)
        return float(upper_integral - lower_integral)

    def probability_of_x_from_a_to_b(self, a, b, lower_bound=None):
        lower_bound = set_default_value(lower_bound, self._lower_bound)
        integral_of_a = self.cumulative_density_function(lower_bound, a)
        integral_of_b = self.cumulative_density_function(lower_bound, b)
        # We could return all of this as a tuple if we want the intermediate values too
        return float(integral_of_b - integral_of_a)

    def probability_of_at_least_x(self, x, lower_bound=None):
        lower_bound = set_default_value(lower_bound, self._lower_bound)
        return self.cumulative_density_function(lower_bound, x)

    def probability_greater_than_x(self, x, lower_bound=None):
        lower_bound = set_default_value(lower_bound, self._lower_bound)
        return 1 - self.probability_of_at_least_x(x, lower_bound)

    def get_expected_value(self, exponent=1):
        x, y, z = symbols("x y z")
        new_function = "(x**" + str(exponent) + ")*(" + self._integratable_string + ")"
        mu = integrate(new_function, (x, self._lower_bound, self._upper_bound))
        try:
            mu = float(mu)
        except TypeError:
            print(f"Here's the problem {mu}")
            mu = float(mu.evalf())
        if not isinstance(mu, float):
            print(mu)
            print("integration failed")
            return None
        return mu

    def get_variance(self):
        return self.get_expected_value(2) - self._expected_value ** 2

    def get_percentile(self, percentile, lower_bound=None):
        lower_bound = set_default_value(lower_bound, self._lower_bound)
        return_value = None
        x, y, z = symbols("x y z")
        if percentile > 1:
            percentile = percentile / 100
        lower_val = self._indef_integral.subs(x, 0)
        # Find the x value for which the integrated function equals the percentile
        new_equation = (self._indef_integral.doit() - lower_val) - percentile  # Does thisoverwrite indef_integral?
        value = solveset(new_equation, x)
        for num in value:
            if num > lower_bound and num < self._upper_bound:
                return_value = num
                break
        return return_value

    def validate_function(self):
        parentheses = 0
        previous_character = None
        self._variables = None
        variables = set()
        for char in self._function_string:
            if char not in "0123456789()+-/*^epxyz":
                return False
            if char == '(':
                parentheses += 1
            elif char == ')':
                parentheses -= 1
            elif char in '+-/^*':
                if previous_character in '+-/^*':
                    print("2 operators are adjacent")
                    return False
            elif char in 'ep':
                if previous_character not in '+-/^*()':
                    print("numeric adjacent to e or p, need an operator")
                    return False
            else:
                # if the character is a number
                if previous_character in 'ep':
                    print("numeric adjacent to e or p, need an operator")
                    return False
                if char in 'xyz':
                    # Find how many variables there are
                    variables.add(char)
            previous_character = char
            # Check for parenthis closing, no dangling operators, no paird operators, no e2 etc
        if parentheses != 0:
            print("Parentheses were not paired!")
            return False
        if self._function_string[0] in '+-/^*' or self._function_string[-1] in '+-/^*':
            print("Function started or ended with an operator")
            return False
        self._variables = variables
        return True

    def read_function(self):
        self._postfix_function = read_infix_function(self._function_string)

    def read_postfix_function(self, *args):
        return eval_postfix_function(self._postfix_function,*args)


class Gamma_distribution(Distribution):

    def __init__(self, alpha, beta):
        self._alpha = alpha
        self._beta = beta
        self._gamma = gamma_function(self._alpha)
        self._expected_value = alpha * beta
        self._variance = alpha * beta ** 2

    def probability_density_function(self, x):
        value = 1 / (self._beta ** self._alpha * self._gamma) * x ** (self._alpha - 1) * exp(-x / self._beta)
        return value
