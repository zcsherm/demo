from probability_distributions import *

class Function_probability:
    
    """
        Represents a distribution that is defined by an arbitrary function. The function must be passed as a string with specific requirements. 
    """
    
    def __init__(self, function_string=None, lower_bound=0, upper_bound=oo):
        """
        Initializes a distribution defined by an arbitrary function. If a string is not passed, will prompt user for one.
        function_string: A string describing the function, must only contain 0-9,(),+-*/^,e,p=pi,x,y,and z
        lower_bound: the lower bound that the distribution is defined for. 0 by default
        upper_bound: The upper bound that the distribution is defined for. infinity by default
        """
        if function_string is None:
            # prompt user to enter a function
            self.get_function()
        else:
            self._function_string = function_string

        # Interprete the string into postfix notation
        self.read_function()
        self._lower_bound = lower_bound
        self._upper_bound = upper_bound

        # Integrate the function and save that as an attribute
        self.get_cdf_function()
        self._expected_value = self.get_expected_value()
        self._variance = self.get_variance()
        

    def get_function(self, function_string=None):
        """
        Prompt the user to enter a string that represents a mathematical function. Valid inputs include 0-9, 'e' as euler's number, 'p' as pi, x, y, or z as variables, and any of the following operators: +-*/^(). Note that a caret is used
        to denote exponentiation.
        """
        # Get the function written as a string, e = e, p = pi, xyz can be variables
        if function_string is None:
            self._function_string = input("Please enter a function using 0-9,()+-/*^,e,p,xyz: ").strip()
            
            # Validate that the string was interpretable.
            while not self.validate_function():
                self._function_string = input(
                    "The function you entered had an invalid character, please enter a function using 0-9,()+-/*^,e,p,xyz: ").strip()
        else:
            self._function_string = function_string

    def get_cdf_function(self):
        """
        Gets the indefinite integral for the probability density function. Currently only supports x as a variable of integration.
        """
        x, y, z = symbols("x y z")
        integratable_string = ""
        # Replace characters in passed string with symbols that are interpretable by python
        integratable_string = self._function_string.replace("^", "**")
        integratable_string = integratable_string.replace('p', "pi")
        integratable_string = integratable_string.replace('e', "exp(1)")
        self._integratable_string = integratable_string
        self._indef_integral = integrate(integratable_string, x)

    def probability_mass_function(self, *args):
        # Potentially run a limit as it approaches the passed arg? Not extremely useful
        pass

    def cumulative_density_function(self, lower_bound=None, upper_bound=None, *args, **kwargs):
        """
        Integrates the pdf from the lower_bound to the upper_bound.
        :lower_bound: The lower limit of integration
        :upper_bound: The upper limit of integration
        """
        # Set limits to default bounds of the function if they were not specified
        lower_bound = set_default_value(lower_bound, self._lower_bound)
        upper_bound = set_default_value(upper_bound, self._upper_bound)

        # Solve the upper and lower integral and return the result
        x, y, z = symbols("x y z")
        upper_integral = self._indef_integral.subs(x, upper_bound)
        lower_integral = self._indef_integral.subs(x, lower_bound)
        return float(upper_integral - lower_integral)

    def probability_of_x_from_a_to_b(self, a, b, lower_bound=None):
        """
        Gets the probability that x falls between a and b.
        :a: the lower bound of the interval
        :b: the upper bound of the interval
        :lower_bound: the lower_bound of the function as a whole
        """
        lower_bound = set_default_value(lower_bound, self._lower_bound)
        integral_of_a = self.cumulative_density_function(lower_bound, a)
        integral_of_b = self.cumulative_density_function(lower_bound, b)
        # We could return all of this as a tuple if we want the intermediate values too
        return float(integral_of_b - integral_of_a)

    def probability_of_at_most_x(self, x, lower_bound=None):
        """
        Gets the probability that the function returns at x or less.
        :x: The maximum value that we are considering in the probability
        :lower_bound: Ther lower bound of the function
        """
        lower_bound = set_default_value(lower_bound, self._lower_bound)
        return self.cumulative_density_function(lower_bound, x)

    def probability_greater_than_x(self, x, lower_bound=None):
        """
        Gets the probability that the function returns a value greater than x
        :x: The lowest bound of the probability range
        :lower_bound: The lower bound of the function
        """
        lower_bound = set_default_value(lower_bound, self._lower_bound)
        return 1 - self.probability_of_at_most_x(x, lower_bound)

    def get_expected_value(self, exponent=1):
        """
        Gets the expected value for the function. Integrates the function: x^exponent * f(x)
        :exponent: the power to raise x to before integration 
        """
        x, y, z = symbols("x y z")
        
        # add 'x**1*' or 'x**2*', etc, to the front of the integratable function
        new_function = "(x**" + str(exponent) + ")*(" + self._integratable_string + ")"
        mu = integrate(new_function, (x, self._lower_bound, self._upper_bound))

        # Check that the integration succeeded and didn't return another expression
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
        """
        Gets the variance for the function by calculating E(x^2) - E(x)
        """
        return self.get_expected_value(2) - self._expected_value ** 2

    def get_percentile(self, percentile, lower_bound=None):
        """
        Finds the value that represents a passed percentile for the function
        :percentile: The percentile for which we want the x value
        """
        # Set lower_bound to the default if it wasn't passed
        lower_bound = set_default_value(lower_bound, self._lower_bound)
        return_value = None
        x, y, z = symbols("x y z")
        
        # Check if the percentile was written as a whole number or a decimal, ie .9 vs 90
        if percentile > 1:
            percentile = percentile / 100

        # Get the value of the integral at 0, which should be 0
        lower_val = self._indef_integral.subs(x, 0)

        # setup a new equation: Integral(f(x)) - percentile = 0
        new_equation = (self._indef_integral.doit() - lower_val) - percentile
        
        # solve for x, may return multiple solutions
        value = solveset(new_equation, x)

        # iterate through each solution and get the value that is within the bounds of the function
        for num in value:
            if num > lower_bound and num < self._upper_bound:
                return_value = num
                break
        return return_value

    def validate_function(self):
        """
        Checks the function string entered by the user and validates each character.
        """
        # Setup metrics for validity
        parentheses = 0
        previous_character = None
        self._variables = None
        variables = set()

        # Check each character
        for char in self._function_string:
            if char not in "0123456789()+-/*^epxyz":
                return False
            
            # Make sure that all parentheses are closed when the function is over
            if char == '(':
                parentheses += 1
            elif char == ')':
                parentheses -= 1
            
            elif char in '+-/^*':
                
                # Make sure that there are not operators back to back, ie '4+/5
                if previous_character in '+-/^*':
                    print("2 operators are adjacent")
                    return False
                    
            elif char in 'ep':
                
                # Check that the user didn't enter something like '5e+2p'. Must be '5*e+2*p'
                if previous_character not in '+-/^*()':
                    print("numeric adjacent to e or p, need an operator")
                    return False
                    
            else
            
                # check that the user didn't enter something like 'e5'
                if previous_character in 'ep':
                    print("numeric adjacent to e or p, need an operator")
                    return False
                
                if char in 'xyz':
                    # Find how many variables there are
                    variables.add(char)  
            previous_character = char

        if parentheses != 0:
            print("Parentheses were not paired!")
            return False
            
        # Check that the function did not begin with or end with an operator    
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
    
    """
    Represents a gamma distribution
    """
    def __init__(self, alpha, beta):
        """
        Initialize a gamma distribution with the passed alpha and beta values
        :alpha: the alpha value for the distribution
        :beta: the beta, or scale, value for the distribution. Rate must be passed as 1/rate
        """
        self._alpha = alpha
        self._beta = beta
        self._rate = 1/beta
        self._gamma = gamma_function(self._alpha)
        self._expected_value = alpha * beta
        self._variance = alpha * beta ** 2

    def probability_density_function(self, x):
        """
        Returns the pdf of the gamma function at a given value
        :x: the value to be plugged in
        """
        value = 1 / (self._beta ** self._alpha * self._gamma) * x ** (self._alpha - 1) * exp(-x / self._beta)
        return value

    def cumulative_density_function(self,x):
        """
        Returns the cumulative probability of x. Uses Riemann sums of the incomplete gamma function to ffind the area under the curve.
        """
        return incomplete_gamma_function(self._alpha,self._rate*x) / self._gamma

    def get_expected_value(self):
        return self._alpha * self._beta

    def get_variance(self):
        return self._alpha * self._beta **2

    def probability_of_x_from_a_to_b(self, a, b):
        return self.cumulative_density_function(b)-self.cumulative_density_function(a)

    def probability_of_at_least_x(self, x):
        return self.cumulative_density_function(x)

    def probability_greater_than_x(self, x):
        return 1 - self.probability_of_at_least_x(x)

class Chi_Squared(Gamma_distribution):

    def __init__(self,v):
        super().__init__(v/2,2)
        self._v = v
