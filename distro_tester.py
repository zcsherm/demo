import unittest
from main import *

class MyTestCase(unittest.TestCase):
    def test_something(self):
        #self.assertEqual(True, False)  # add assertion here
        pass
    def test_choose(self):
        print(choose(5,3))

    def test_fact(self):
        print(factorial(8))

    def test_binom(self):
        bd = Binomial_distribution(5,.4)
        print(bd.probability_mass_function(3))
        print(bd.cumulative_mass_function(3))
        print(bd.find_percentile(90))

    def test_poisson(self):
        pd = Poisson_distribution(8)
        print(pd.probability_mass_function(6))
        print(pd.cumulative_mass_function(6))
        print(pd.find_percentile(32))

    def test_function_distro(self):
        test_funcs = {"1+2-3*(6-10)/5":1+2-3*(6-10)/5,
                      "134/43+14^2-1":134/43+14**2-1,
                      "e+3-2*0":exp(1)+3-2*0,
                      'p^2*3*e':pi**2*3*exp(1),
                      'e^(10-2)/(3-(2*5))+1':exp(10-2)/(3-(2*5))+1}

        test_vari_funcs = {"x^2+3":lambda x: x**2+3,
                           "1+2-3*(x-10)/5": lambda x: 1 + 2 - 3 * (x - 10) / 5,
                           "x/43+14^x-x":lambda x: x / 43 + 14 ** x - x,
                           "e+x-2*0": lambda x: exp(1) + x - 2 * 0,
                           'p^x*3*e': lambda x: pi ** x * 3 * exp(1),
                           'e^(x)/(3-(2*5))+1': lambda x: exp(x) / (3 - (2 * 5)) + 1}

        func_string = "1+2-3*(6-10)/5"
        fd = Function_probability(func_string)
        #print(fd._postfix_function)
        #print(fd.read_postfix_function())
        self.assertAlmostEqual((1+2-3*(6-10)/5),fd.read_postfix_function())
        for func in list(test_funcs.keys()):
            fd = Function_probability(func)
            self.assertAlmostEqual(fd.read_postfix_function(),test_funcs[func])
            print(f"Function {func} == {fd.read_postfix_function()}")
        for func in list(test_vari_funcs.keys()):
            fd = Function_probability(func)
            for i in range(1,6):
                fd_value = fd.read_postfix_function(i)
                calcd_value = test_vari_funcs[func](i)
                self.assertAlmostEqual(fd_value,calcd_value)
                print(f"Function {func} == {fd_value}")

if __name__ == '__main__':
    unittest.main()
