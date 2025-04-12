from math import exp, pi
from sympy import integrate, symbols, oo
from sympy.solvers import solveset



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


def set_default_value(parameter,argument):
    if parameter is None:
        return argument
    return parameter

def read_infix_function(function_string):
    # iterate the function string and convert it to postfix notation
    # Ex. 1+3*4-(3*5)+2^6-1 -> 134*+35*-26^+1-
    operator_stack = []
    output_stack = []
    current_number = None
    for char in function_string:
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
    return output_stack

def eval_postfix_function(post_fix_equation,*args):
    """
    Reads a postfix equation (formatted as a list) and evaluates it
    :param post_fix_equation: The post-fix formatted list
    :param args: Assignments for variables in the order x, y, z. y=4,x=2 would be func(equation,2,4)
    :return: The result of the evaluation
    """
    stack = []
    for value in post_fix_equation:
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

