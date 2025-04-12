from probability_distributions import *


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

    def probability_of_at_least_x(self, x):
        return self.cumulative_mass_function(x)

    def probability_greater_than_x(self, x):
        return 1 - self.cumulative_mass_function(x)

    def probability_greater_than_equal_to_x(self, x):
        return 1 - self.cumulative_mass_function(x - 1)

    def probability_less_than_x(self, x):
        return 1 - self.cumulative_mass_function(x - 1)

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
                index = max(((end - index) // 2), 1) + start
            else:
                current_closest = index, prob_of_index
                end = index
                index = max(((end - index) // 2), 1) + start
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

    def probability_of_at_least_x(self, x):
        return self.cumulative_mass_function(x)

    def probability_greater_than_x(self, x):
        return 1 - self.cumulative_mass_function(x)

    def probability_greater_than_equal_to_x(self, x):
        return 1 - self.cumulative_mass_function(x - 1)

    def probability_less_than_x(self, x):
        return self.cumulative_mass_function(x - 1)

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
                index = max(((end - index) // 2), 1) + floor
            else:
                current_closest = index, prob_of_index
                end = index
                index = max(((end - index) // 2), 1) + floor
            if index == end:
                break
        return current_closest


class Distribution_table(Distribution):
    # Models discrete probabilities where the probability at each payout is an integer x representing x/(sum(xi) chance of occurence
    def __init__(self, probabilities=None):
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
        print(
            "We're going to build the probabilities for discrete events. I'm going to ask for first the payout or event, and then the probability. press 'q' to indicate you are finished")
        while key != 'q':
            while key is None:
                key = input("What is the event (payout)?: ")
                if key == 'q':
                    break
                try:
                    key = float(key)
                except ValueError:
                    key = None
                    print("Please enter a number.")
            while value is None:
                value = input(
                    f"What is the probability of {key}? Must be an integer representing proportion of sample space.")
                try:
                    value = int(value)
                    if value < 0:
                        value = None
                        print("Your probability was smaller than 1, try again")
                except ValueError:
                    value = None
                    print("Your decimal was invalid")
                self.add_outcome(key, value)

    def add_outcome(self, event, value):
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

    def probability_mass_function(self, event):
        try:
            return self._probabilities[event] / self._sample_space_size
        except KeyError:
            return 0

    def get_expected_value(self, exponent=1):
        total = 0
        for key in list(self._probabilities.keys()):
            total += (key ** exponent) * self.probability_mass_function(key)
        return total

    def get_variance(self):
        # E(x^2)- E(x)^2
        e_x_squared = self.get_expected_value(exponent=2)
        e_squared = self._expected_value ** 2
        return e_x_squared - e_squared

    def get_standard_deviation(self):
        return self._variance ** .5

    def linear_combination(self, a, b):
        lc_expected = a * self._expected_value + b
        lc_variance = a ** 2 * self._variance
        print(f"The expected value of the linear combination W={a}X+{b} is: {lc_expected}")
        print(f"The variance of the linear combination w={a}X+{b} is: {lc_variance}")

distributions = {"binomial": Binomial_distribution,
                 "poisson": Poisson_distribution
                 }