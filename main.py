# I think the basic elements of the programming should be:
# asks if they know the distribution type
# Get distribution type
# Get necessary params
# Create an object of that model
# Get vals like percentiles and sd's etc and store as attributes
# Plot the graph
# Keep the obj in memory and let user query items, like prob for ranges, etc


from math import exp, pi
from sympy import integrate, symbols, oo
from sympy.solvers import solveset
#from sympy.core import subs
from fraction import Fraction


# map distrobutions to reps for their binomial function (change to LaTex or images?
pmf_descriptions = {"Binomial": "(n choose x)*(probability^x)*(1-probability)^(n-x)",
                    "Poisson": "((lambda^x)*(e^-lambda))/x!"}

# Save calculated choose values and factorials, pickle these later?
choose_memos = {}
factorial_memos = {0: 1}

# Character map, simplifies string to equation process
char_map = {}

# infix precedence
infix_precedence = {'+': 1,
                    '-': 1,
                    '*': 2,
                    '/': 2,
                    '^': 3,
                    '(':0}



class Model:

    # Represents a situation that can use a distribution to model its properties
    def __init__(self, distribution_type):
        # Initialize the model
        # get it's string version
        self._distribution = distribution_type.lower()
        self._distribution_func = distributions[distribution_type.lower()]()


class Distribution:

    # Models a binomial distribution of n binary bernoulli trials with p chance of success
    def __init__(self):
        pass

    def get_standard_attributes(self):
        # allow for calling on mu or expected
        self._mu = self._expected
        self._standard_deviation = self._variance ** .5


class Binomial_distribution(Distribution):

    def __init__(self, trials=None, probability=None):
        while trials <= 0 or probability is None:
            print("The number of trials is invalid, please enter a number greater than 0")
            trials = input("How many trials are in this series?: ")

        while probability < 0 or probability > 1 or probability is None:
            print("The probability is invalid, please enter a number between 0 and 1")
            probability = input("What is the probability of success for this series?: ")

        self._trials = trials
        self._probability = probability
        self._probability_mass_function = pmf_descriptions["Binomial"]
        self._variance = self._trials * self._probability * (1 - self._probability)
        self._expected = self._trials * self._probability

        self.get_standard_attributes()  # Get common distribution elements from parent

    def probability_mass_function(self, successes):
        return choose(self._trials, successes) * (self._probability ** successes) * (
                    (1 - self._probability) ** (self._trials - successes))

    def cumulative_mass_function(self, successes):
        total = 0
        for i in range(successes + 1):
            total += self.probability_mass_function(i)
        return total

    def probability_of_at_least_x(self,x):
        return self.cumulative_mass_function(x)

    def probability_greater_than_x(self,x):
        return 1-self.cumulative_mass_function(x)

    def probability_greater_than_equal_to_x(self,x):
        return 1-self.cumulative_mass_function(x-1)

    def probability_less_than_x(self,x):
        return 1-self.cumulative_mass_function(x-1)
        
    def find_percentile(self, percentile):
        # find the number of successes that represents the percentile of the whole distro
        # use a binary search, return the first success that is >= requested percentile
        current_closest = None
        index = self._trials // 2
        end = self._trials
        start = 0
        while end - index is not 0:
            prob_of_index = self.cumulative_mass_function(index)
            if prob_of_index == percentile / 100:
                return index, prob_of_index
            if prob_of_index < percentile / 100:
                start = index
                index = max(((end - index) // 2),1) + start
            else:
                current_closest = index, prob_of_index
                end = index
                index = max(((end - index) // 2),1) + start
        return current_closest


class Poisson_distribution(Distribution):

    def __init__(self, rate=None):
        # lambda is rate, count per space or time
        while rate <= 0:
            print("The rate parameter was invalid, please enter a number greater than 0")
            rate = input("What is the rate of occurence for this event? (count per space or time): ")
        self._rate = rate
        self._lambda = rate
        self._expected = self._lambda
        self._variance = self._lambda
        self._probability_mass_function = pmf_descriptions["Poisson"]

        self.get_standard_attributes()
        
    def probability_of_at_least_x(self,x):
        return self.cumulative_mass_function(x)

    def probability_greater_than_x(self,x):
        return 1-self.cumulative_mass_function(x)

    def probability_greater_than_equal_to_x(self,x):
        return 1-self.cumulative_mass_function(x-1)

    def probability_less_than_x(self,x):
        return 1-self.cumulative_mass_function(x-1)
    
    def probability_mass_function(self, occurences):
        numerator = self._lambda ** occurences * exp(-self._lambda)
        denominator = factorial(occurences)
        return numerator / denominator

    def cumulative_mass_function(self, occurences):
        total = 0
        for i in range(occurences + 1):
            total += self.probability_mass_function(i)
        return total

    
    def find_percentile(self, percentile):
        # Find the bounds of the range by finding k such that the 2^k < n < 2^(k+1)
        start = 1
        floor = 0
        prob_at_index = self.cumulative_mass_function(start)
        while prob_at_index <= percentile / 100:
            floor = start
            start *= 2
            prob_at_index = self.cumulative_mass_function(start)
        current_closest = start, prob_at_index
        end = start
        index = (end - floor) // 2 + floor
        # Perform a binary search on that range, refactor? into parent method?
        while end - floor > 0:
            prob_of_index = self.cumulative_mass_function(index)
            if prob_of_index == percentile / 100:
                return index, prob_of_index
            if prob_of_index < percentile / 100:
                floor = index
                index = max(((end - index) // 2),1) + floor
            else:
                current_closest = index, prob_of_index
                end = index
                index = max(((end - index) // 2),1) + floor
            if index == end:
                break
        return current_closest


class Distribution_table(Distribution):
    # Models discrete probabilities where the probability at each payout is an integer x representing x/(sum(xi) chance of occurence
    def __init__(self,probabilities=None):
        if probabilities is None:
            self.get_probabilities()
        else:
            self._probabilities = probabilities
        self.find_sample_space_size()
        self._variability = self.get_variance()
        self._expected_value = self.get_expected_value()
        self._standard_deviation = self.get_standard_deviation()
    
    def get_probabilities(self):
        self._probabilities = {}
        key = None
        value = None
        print("We're going to build the probabilities for discrete events. I'm going to ask for first the payout or event, and then the probability. press 'q' to indicate you are finished")
        while key != 'q':
            while key is None:
                key=input("What is the event (payout)?: ")
                if key == 'q':
                    break
                try:
                    key=float(key)
                except ValueError:
                    key = None
                    print("Please enter a number.")
            while value is None:
                value = input(f"What is the probability of {key}? Must be an integer representing proportion of sample space.")
                try:
                    value=int(value)
                    if value < 0:
                        value = None
                        print("Your probability was smaller than 1, try again")
                except ValueError:
                    value = None
                    print("Your decimal was invalid")
                self.add_outcome(key,value)

    def add_outcome(self,event,value):
        try:
            self._probabilities[event] += value
        except KeyError:
            self._probabilities[event] = value

    def find_sample_space_size(self):
        number_of_distinct_events = 0
        number_of_possibilities = 0
        for key in list(self._probabilities.keys()):
            number_of_distinct_events += 1
            number_of_possibilities += self._probabilities[key]
        self._distinct_events = number_of_distinct_events
        self._sample_space_size = number_of_possibilities
        self._expected_value = self.get_expected_value()
        self._variance = self.get_variance()


    def probability_mass_function(self,event):
        try:
            return self._probabilities[event]/self._sample_space_size
        except KeyError:
            return 0

    def get_expected_value(self, exponent = 1):
        total = 0
        for key in list(self._probabilities.keys()):
            total += (key**exponent)*self.probability_mass_function(key)
        return total

    def get_variance(self):
        # E(x^2)- E(x)^2
        e_x_squared = self.get_expected_value(exponent=2)
        e_squared = self._expected_value ** 2
        return e_x_squared - e_squared

    def get_standard_deviation(self):
        return self._variance ** .5

    def linear_combination(self,a,b):
        lc_expected = a* self._expected_value + b
        lc_variance = a**2 * self._variance
        print(f"The expected value of the linear combination W={a}X+{b} is: {lc_expected}")
        print(f"The variance of the linear combination w={a}X+{b} is: {lc_variance}")
        
class Function_probability:
    # Represents when the probability is a function
    def __init__(self,function_string=None,lower_bound=0,upper_bound=oo):
        if function_string is None:
            self.get_function()
        else:
            self._function_string=function_string
        self.read_function()
        self._lower_bound = lower_bound
        self._upper_bound = upper_bound
        self.get_cdf_function
        self._expected_value = self.get_expected_value()
        self._variance = self.get_variance()
        self.get_standard_attributes()
        
    def get_function(self,function_string=None):
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
        integratable_string = self._function_string.replace("^","**")
        integratable_string = self._function_string.replace('e',"exp(1)")
        integratable_string = self._function_string.replace('p',"pi")
        self._integratable_string = integratable_string
        self._indef_integral = integrate(integratable_string,x)
    
    def probability_mass_function(self, *args):
        # Integration
        # Potentially run a limit as it approaches the passed arg?
        pass

    def cumulative_density_function(self,lower_bound=None,upper_bound=None,*args,**kwargs):
        lower_bound=(lower_bound,self._lower_bound)
        upper_bound=(upper_bound,self._upper_bound)
        x, y, z = symbols("x y z")
        upper_integral = self._indef_integral.subs(x, upper_bound)
        lower_integral = self._indef_integral.subs(x, lower_bound)
        return upper_integral - lower_integral

    def probability_of_x_from_a_to_b(self,a,b,lower_bound=None):
        lower_bound=(lower_bound,self._lower_bound)
        integral_of_a = self.cumulative_density_function(lower_bound,a)
        integral_of_b = self.cumulative_density_function(lower_bound,b)
        # We could return all of this as a tuple if we want the intermediate values too
        return integral_of_b - integral_of_a

    def probability_of_at_least_x(self,x,lower_bound=None):
        lower_bound=set_default_value(lower_bound,self._lower_bound)
        return self.cumulative_density_function(lower_bound,x)

    def probability_greater_than_x(self,x,lower_bound=None):
        lower_bound = set_default_value(lower_bound, self._lower_bound)
        return 1-self.probability_of_at_least_x(x,lower_bound)

    def get_expected_value(self, exponent=1):
        x,y,x = symbols("x y z")
        new_function = "(x**"+str(exponent)+")*(" + self._integratable_string + ")"
        mu = integrate(new_function, (x,self._lower_bound,self._upper_bound))
        if not isinstance(mu,float):
            print("integration failed")
            return None
        return mu

    def get_variance(self):
        return self.get_expected_value(2) - self._expected_value

    def get_percentile(self,percentile,lower_bound=None):
        lower_bound = set_default_value(lower_bound, self._lower_bound)
        x, y, z = symbols("x y z")
        if percentile > 1:
            percentile = percentile / 100
        lower_val = self._indef_integral.subs(x,0)
        # Find the x value for which the integrated function equals the percentile
        new_equation = (self._indef_integral.doit()-lower_val) - percentile # Does thisoverwrite indef_integral?
        value = solveset(new_equation,x)
        return value
        
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
        # iterate the function string and convert it to postfix notation
        # Ex. 1+3*4-(3*5)+2^6-1 -> 134*+35*-26^+1-
        operator_stack = []
        output_stack = []
        current_number = None
        for char in self._function_string:
            # Read the string
            try:
                # If the characer is a numeric, add it to 10* current total
                digit = int(char)
                if current_number is None:
                    current_number = 0
                current_number = current_number * 10 + digit
            except ValueError:
                # If the char is non-numeric, check if the character is a variable
                if char in 'epxyz':
                    current_number = char

                else:
                    # If the char is a symbol, then output our current number total
                    if current_number is not None:
                        output_stack.append(current_number)
                        current_number = None
                    if len(operator_stack) == 0:
                        operator_stack.append(char)
                    else:
                        # We need to check the precedence of all the operators currently in the stack
                        if char == '(':
                            operator_stack.append(char)
                        elif char == ')':
                            token = operator_stack[-1]
                            while token != '(':
                                output_stack.append(operator_stack.pop())
                                token = operator_stack[-1]
                            # get rid of the ( parenthesis from the stack
                            operator_stack.pop()
                        else:
                            while infix_precedence[char] <= infix_precedence[operator_stack[-1]]:
                                output_stack.append(operator_stack.pop())
                                if len(operator_stack) == 0:
                                    break
                            operator_stack.append(char)

        # Output the final read number
        if current_number is not None:
            output_stack.append(current_number)
        # empty the operator stack
        while len(operator_stack) > 0:
            output_stack.append(operator_stack.pop())
        self._postfix_function = output_stack

    def read_postfix_function(self, *args):
        stack = []
        for value in self._postfix_function:
            if isinstance(value, int):
                stack.append(value)
            else:
                if value in 'xyz':
                    stack.append(args['xyz'.index(value)])
                elif value in 'ep':
                    stack.append(value)
                else:
                    second_operand = stack.pop()
                    first_operand = stack.pop()
                    if second_operand == 'e':
                        second_operand = exp(1)
                    elif second_operand == 'p':
                        second_operand = pi
                    if first_operand == 'e':
                        first_operand = exp(1)
                    elif first_operand == 'p':
                        first_operand = pi

                    # switch case for operator
                    if value == '+':
                        result = first_operand + second_operand
                    elif value == '-':
                        result = first_operand - second_operand
                    elif value == '/':
                        result = first_operand / second_operand
                    elif value == '*':
                        result = first_operand * second_operand
                    elif value == '^':
                        result = first_operand ** second_operand
                    stack.append(result)
        if len(stack) != 1:
            print('I messed this up...')
        return stack[0]


class Gamma_distribution(Distribution):

    def __init__(self,alpha,beta):
        self._alpha = alpha
        self._beta = beta
        self._gamma = gamma_function(self._alpha)
        self._expected_value = alpha * beta
        self._variance = alpha * beta**2

    def probability_density_function(self,x):
        value = 1/(self._beta**self._alpha*self._gamma)*x**(self._alpha-1)*exp(-x/self._beta)

def factorial(num):
    # Ensure that the passed value is an integer
    if not isinstance(num, int):
        # Add an error
        print("The number is not an integer, please double check the input")
        return

    # Ensure that the value is not negative
    if num < 0:
        # Add an error
        print("The number is negative, please double check the input")
        return

    # Check if we memo'd the functions
    if num in factorial_memos:
        return factorial_memos[num]
    total = num * factorial(num - 1)
    factorial_memos[num] = total
    return total


def choose(total_options, number_chosen):
    if (total_options, number_chosen) in choose_memos:
        return choose_memos[(total_options, number_chosen)]
    numerator = factorial(total_options)
    # Denom is more efficitent when passign the smallest
    denominator = factorial(number_chosen) * factorial(total_options - number_chosen)
    choose_memos[(total_options, number_chosen)] = numerator / denominator
    return numerator / denominator

def gamma_function(num):
    x = symbols('x')
    if num < 0:
        print("Gamma failed")
        return
    if isinstance(num,int):
        return factorial(num-1)
    else:
        val = integrate(x^(num-1)*exp(-x),(x,0,oo))
        return val

# map string values to the classses for each distro
distributions = {"binomial": Binomial_distribution,
                 "poisson": Poisson_distribution
                 }

def set_default_value(parameter,argument):
    if parameter is None:
        return argument
    return parameter