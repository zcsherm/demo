# I think the basic elements of the programming should be:
# asks if they know the distribution type
# Get distribution type
# Get necessary params
# Create an object of that model
# Get vals like percentiles and sd's etc and store as attributes
# Plot the graph
# Keep the obj in memory and let user query items, like prob for ranges, etc


from math import exp, pi
from sympy import integrate


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
                    '^': 3}



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
        return choose(self._trials, successes) * (self._probabilty ** successes) * (
                    (1 - self._probability) ** self._trials - successes)

    def cumulative_mass_function(self, successes):
        total = 0
        for i in range(successes + 1):
            total += self.probability_mass_function(i)
        return total

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
                index = ((end - index) // 2) + start
            else:
                current_closest = index, prob_of_index
                end = index
                index = ((end - index) // 2) + start
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
                start = index
                index = ((end - index) // 2) + start
            else:
                current_closest = index, prob_of_index
                end = index
                index = ((end - index) // 2) + start
        return current_closest


class Function_probability:
    # Represents when the probability is a function
    def __init__(self):
        self.get_function()

    def get_function(self):
        # Get the function written as a string, e = e, p = pi, xyz can be variables
        self._function_string = input("Please enter a function using 0-9,()+-/*^,e,p,xyz: ").strip()
        while not self.validate_function():
            self._function_string = input(
                "The function you entered had an invalid character, please enter a function using 0-9,()+-/*^,e,p,xyz: ").strip()
        self.read_function()

    def probability_mass_function(self, *args):
        # Integration
        pass

    def validate_function(self):
        parentheses = 0
        previous_character = None
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
            previous_character = char
            # Check for parenthis closing, no dangling operators, no paird operators, no e2 etc
        if parentheses != 0:
            print("Parentheses were not paired!")
            return False
        if self._function_string[0] in '+-/^*' or self._function_string[-1] in '+-/^*':
            print("Function started or ended with an operator")
            return False
        return True

    def read_function(self):
        # iterate the function string and convert it to postfix notation
        # Ex. 1+3*4-(3*5)+2^6-1 -> 134*+35*-26^+1-
        operator_stack = []
        output_stack = []
        current_number = 0
        for char in self._function_string:
            # Read the string
            try:
                # If the characer is a numeric, add it to 10* current total
                digit = int(char)
                current_number = current_number * 10 + digit
            except ValueError:
                # If the char is non-numeric, check if the character is a variable
                if char in 'epxyz':
                    current_number = char

                else:
                    # If the char is a symbol, then output our current number total
                    output_stack.append(current_number)
                    current_number = 0
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
                        second_operand = pi()
                    if first_operand == 'e':
                        first_operand = exp(1)
                    elif first_operand == 'p':
                        first_operand = pi()

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
    if [total_options, number_chosen] in choose_memos:
        return choose_memos[[total_options, number_chosen]]
    numerator = factorial(total_options)
    # Denom is more efficitent when passign the smallest
    denominator = factorial(number_chosen) * factorial(total_options - number_chosen)
    choose_memos[[total_options, number_chosen]] = numerator / denominator
    return numerator / denominator

# map string values to the classses for each distro
distributions = {"binomial": Binomial_distribution,
                 "poisson": Poisson_distribution
                 }