# Class representing a singles sample 
from math import floor
import scipy.stats as st
# Now that I'm just gonna use scipy, might as well change z score table to a function
CONFIDENCE_Z_SCORES = {.9:1.645,
                      .95:1.96,
                      .99:2.576}
class Sample:
    """
    Represents a sample of data points. Can have labels for each point or not.
    """
    def __init__(self,data_set, labels=None):
        """
        Initialize a new sample of data.
        :data_set: The response from each experimental unit
        :labels: A label or name for each experimental unit, defaults to 1-indexed value
        """
        if labels is None:
            # if labels wasn't passed, instead make a label for each data point based on which sample it is
            labels = []
            for i in range(len(data_set)):
                labels.append(i+1)
        # Zip the labels and data together and then sort and unzip them.
        zipped = zip(data_set, labels)
        zipped = sorted(zipped)
        samples, labels = zip(*zipped)
        self._samples = list(samples)
        self._labels = list(labels)
        self._count = len(data_set)

    def add_sample(self,data_point,label=None):
        # Doesn't preserve sorted order and causes issues, need to make a sort function that zips each data set together again.
        self._samples.append(data_point)
        self._count += 1
        if label is None:
            label = len(self._labels)
        self._label.append(label)

    def get_count(self):
        """
        Returns the number of elements in the data set
        """
        return self._count

    def get_measurement(self,index):
        """
        Returns the (n-1)th data point
        """
        return self._samples[index]

    def get_standard_deviation(self):
        return self._std_dev
    
class ProportionSample(Sample):
    """
    Represents a sample that measures membership in a boolean measurement. Supports proportional calculations.
    """
    def __init__(self,data_set,positive_case=None,labels=None):
        """
        Initialize the sample
        :data_set: The response from each experimental unit
        :labels: The names for each experimental unit
        :positive_case: which response we consider to be positive, or indicate membership
        """
        
        # Initialize the basic elements of the sample
        super().__init__(data_set,labels) 
        self._positive_case = positive_case
        
        # Determine how many datapoints are members of the positive class and what the proportion is
        self._positives = self.find_positives(positive_case)
        self._proportion = self.find_proportion()
        
        # Get the standard deviation
        self._std_dev = self.find_standard_deviation()
        
    def find_positives(self, positive_case=None):
        """
        Counts how many data points are members in the positive class
        :positive_case: Which case we consider to be positive
        """
        if positive_case is None:
            positive_case = self._positive_case
        # count how many data points match the positive case
        total_positive = 0
        for i in range(self._count):
            if self._samples[i] == positive_case:
                total_positive += 1
        return total_positives

    def find_standard_deviation(self, proportion=None):
        """
        Finds the standard deviation for the proportion. Uses the formula: sqrt((p(1-p)/n))
        :proportion: What percent of the sample is positive
        """
        if proportion is None:
            proportion = self._proportion
        return ((proportion*(1-proportion))/n)**.5
        
    def find_proportion(self, positives=None, count=None):
        if positives is None:
            positives = self._positives
        if count is None:
            count = self._count
        return positives/count

    def confidence_interval(self, percentile, print=False):
        """
        Finds the confidence interval for a given confidence level (90%,95%,99%).
        :percentile: The percent of confidence
        :print: debug value
        :return: the lower bound and the higher bound
        """
        if percentile > 1:
            percentile = percentile / 100
        if percentile not in CONFIDENCE_Z_SCORES:
            return None
            
        # Find what the range of values should be, use the sample proportion as point estimate
        low_bound = self._proportion - (self.find_sample_error() * CONFIDENCE_Z_SCORES[percentile])
        upper_bound = self._proportion + (self.find_sample_error() * CONFIDENCE_Z_SCORES[percentile])
        if print:
            print(f"The (percentile*100)% confidence interval for the population proportion is from {low_bound} to {upper_bound}")
        return low_bound, upper_bound

    def perform_z_test(self, claim, alpha, tails=2, print=False, CI=.95):
        """
        Performs a z test on the data set. 
        :claim: what the proposed true proportion is
        :alpha: the significance level (1-confidence)
        :tails: Whether we are concerned with two tailed, right, or left tailed test
        :print: Debug, prints out a statement on the z test
        :CI: The requested confidence interval, defaults to 95%
        """
        # Fix bug for finding left tailed test
        # Find the z statistic and the corresponding p value for the claim
        z_stat = ((self._proportion - claim)/((claim*(1-claim))/self._count)**.5)
        # This calc only works for 2 tailed or right tail test
        p_value = (1- st.norm.cdf(z_stat)) * tails
        if print:
            print(f"The probability that a sample would have a mean of {self._proportion}, when the true mean is {claim}, is {p_value}, for a {tails} tailed test.")
            if p_value < alpha:
                print(f"The null hypothesis of {claim} is rejected at a significance level of {alpha}, from a z-stat of {z-stat}")
            else:
                print(f"We fail to reject the null hypothesis of {claim} at a significance level of {alpha}, from a z-stat of {z-stat}")
            self.confidence_interval(CI, True)
        return p_value
        
    def find_sample_error(self):
        """
        Get the proportions sample error
        """
        return ((self._proportion * (1-self._proportion))/n)**.5

    # Add in a summary function

class QuantSample(Sample):
    """
    Represents a sample of quantitative variables
    """
    def __init__(self,data_set,labels=None):
        """
        Initializes the sample set
        :data_set: The set of data points
        :labels: Names for each experimental unit
        """
        super().__init__(data_set,labels)
        # Get basic attributes for the data_set
        self._mean = self.find_mean()
        self._median = self.find_median()
        self._skew = self.find_skew_amount()
        self._std_dev = self.find_std_dev()
        self._variance = self.find_variance()
        self._IQR_range = self.find_IQR()
        self._low_outliers, self._high_outliers = self.find_outliers() 
        self._pop_std_dev = None
        
    def find_mean(self):
        """
        Get the mean of the data points
        """
        total = 0
        # Not sure why I don't just use Sum or average
        for i in range(self._count):
            total += self._samples[i]
        return total/self._count

    def find_median(self):
        """
        Get the median of the data
        """
        # If there is an even number of elements, get an average of the 2 middle entries
        if self._count % 2 == 0:
            median = (self._samples[(self._count-1)//2]+self._samples[self._count//2])/2
        # If there is an odd number of elements, get the precise middle element
        else:
            median = self._samples[self._count//2]
        return median
        
    def find_skew_amount(self):
        """
        Finds how much the mean is pulled from the median, how much outliers affect data
        """
        # Get how much the mean is pulled from the median
        return self._mean-self._median

    def find_IQR(self):
        """
        Find the IQR range of the data
        """
        # get Q2 position (index +1)
        # If it's even then we get the "average" position
        if self._count % 2 ==0:
            Q2 = ((self._count/2+(self._count+2)//2)/2)
            if floor(Q2) % 2 == 0:
                Q2 = int(Q2)
                # From element 1 to median, if there is an even number of elements, get the average of the middle
                Q1 = (self._samples[(Q2//2)-1] + self._samples[(Q2+2)//2-1])/2
                Q3 = (self._samples[((3*Q2)//2)-1] + self._samples[(3*Q2+2)//2-1])/2
            else:
                # Otherwise we can just get the exact midpoint of each subrange
                Q2 = int(Q2)
                Q1 =self._samples[Q2//2]
                Q3 =self._samples[int(3*(Q2//2)+1)]
        else: 
            Q2 = int((self._count+1)//2)
            if Q2 % 2 ==0:
                # If Q2 is even, then get the exact midpoint of the 2 ranges (Q2 is omitted from each range)
                Q1 = self._samples[(Q2//2)]
                Q3 = self._samples[(3*Q2)//2+1]
            else:
                # Otherwise get the average of the middle entries
                Q1 = (self._samples[int((Q2)//2-1)]+self._samples[int(Q2)//2])/2
                Q3 = (self._samples[int((3*(Q2-1))//2)]+self._samples[int(3*Q2)//2])/2
        self._Q1 = Q1
        self._Q3 = Q3
        return Q3-Q1
             
    def find_std_dev(self):
        """
        Find the standard deviation of the sample. sqrt(1/n*E(x-u)^2)
        """
        # Find the average squared error of each sample - Uses std dev of pop formula
        sum = 0
        for i in range(self._count):
            sum += (self._samples[i]-self._mean)**2
        sum /= self._count
        return sum**.5

    def find_variance(self):
        """
        Get the variance
        """
        return self._std_dev**2

    def find_outliers(self):
        """
        Get which responses are outliers (IQR *1.5)
        """
        low_outliers = []
        high_outliers = []
        lowcutoff = self._Q1-(self._IQR_range *1.5)
        highcutoff = self._Q3 + (self._IQR_range * 1.5)
        # Check each response, add it to the outliers if its beyond one of the ranges
        for i in range(self._count):
            if self._samples[i]<lowcutoff:
                low_outliers.append(self._samples[i])
            if self._samples[i]>highcutoff:
                high_outliers.append(self._samples[i])
        return low_outliers, high_outliers

    def set_population_std_dev(self,std_dev):
        """
        Sets the population standard deviation, if known.
        """
        self._pop_std_dev = std_dev
        
    
    def summary(self):
        """
        Prints a summary of the data, all relevant values.
        """
        print(f"============ Summary of Data for Dataset ================")
        print(f"                    boxplot info")
        print(f"Low outlier: {self._Q1-(1.5*self._IQR_range)} | Q1: {self._Q1} | Median: {self._median} | Q3: {self._Q3} | High Outlier: {self._Q3 +(1.5*self._IQR_range)}\n")
        print(f"                    stats info")
        print(f" Mean: {self._mean} | Median: {self._median} | Standard Deviation of Data: {self._std_dev} | Variance: {self._variance} | Standard Deviation of population: {self._pop_std_dev} Data Points (n) : {self._count}")
        print(f" Skew: {self._skew} | Outliers: {len(self._low_outliers)+len(self._high_outliers)}")
        print(f"Low Outliers: {self._low_outliers}")
        print(f"High Outliers: {self._high_outliers}")
        print("=========================================================")

    def confidence_interval(self, percentile, print =False):
        """
        Get the confidence interval for the true mean, IF the population standard deviation is known
        :percentile: How much of a Confidence interval we want (90%,95%,99%)
        :print: Debug, prints out what the range is
        """
        # Get the confidence interval for a true mean, when population std dev is known
        if percentile > 1:
            percentile = percentile / 100
        if percentile not in CONFIDENCE_Z_SCORES or self._pop_std_dev is None:
            return None
        sigma_hat = self._pop_std_dev/(self._count ** self._count)
        self._margin_of_error = sigma_hat * CONFIDENCE_Z_SCORES[percentile]
        low_bound = self._mean - (sigma_hat * CONFIDENCE_Z_SCORES[percentile])
        upper_bound = self._mean + (sigma_hat * CONFIDENCE_Z_SCORES[percentile])
        if print:
            print(f"The {percentile*100}% confidence interval for the mean is from {low_bound} to {upper_bound} with a margin of error of {self._margin_of_error}")
        return low_bound, upper_bound

    def perform_z_test(self, claim, alpha, tails=2, print=False, CI=.95):
        """
        Perform a z test on the data if the population standard deviation is known
        :claim: What the proposed mean is, null hypothesis
        :alpha: What the signficance level is (1-Conf)
        :tails: Whether we want 2 sided, left or right tailed test. !=, <, >
        :print: Debug, prints out the results of the z test
        :CI: The confidence interval to estimate the mean, defaults to .95
        :return: the p value of the z test
        """
        # If populations standard deviation is known
        if self._pop_std_dev is None:
            return None
        # Correct alpha if input in integer form
        if alpha > 1:
            alpha /= 100
        # Find the z statistic and the p value for that z stat
        z_stat = (self._mean - claim) / (self._pop_std_dev/(self._count**.5))
        # only works for 2 tailed or right tailed test
        p_value = (1- st.norm.cdf(z_stat)) * tails
        if print:
            print(f"The probability that a sample would have a mean of {self._mean}, when the true mean is {claim}, is {p_value}, for a {tails} tailed z-test.")
            if p_value < alpha:
                print(f"The null hypothesis of {claim} is rejected at a significance level of {alpha}, from a z-stat of {z-stat}")
            self.confidence_interval(CI, True)
        return p_value

    def perform_t_test(self,claim,alpha,tails=2,print=False,CI=.95):
        """
        Performs a t test on the data if the population standard deviation is unknown.
        :claim: What the proposed mean is, null hypothesis
        :alpha: The signicanfce level (1-conf)
        :tails: Whether we want a 2 tailed, right, or left test
        :print: debug, prints out results of t test
        :CI: The confidence interval for estimating the mean
        :return: The p value for the t test
        """
        # Get the t stat and p value
        t_stat = (self._mean-claim)/(self.find_standard_error_sample())
        # Change functionality to acount for left tailed tests
        p_value = (1-st.t.cdf(t_stat,self._count-1))*tails
        if print:
            print(f"The probability that a sample would have a mean of {self._mean}, when the true mean is {claim}, is {p_value}, for a {tails} tailed t-test.")
            if p_value < alpha:
                print(f"The null hypothesis of {claim} is rejected at a significance level of {alpha}, from a t-stat of {t-stat}")
            self.confidence_interval(CI, True)
        return p_value
        
    def confidence_interval(self,alpha,print=False):
        """
        Get a confidence interval for the true mean
        :alpha: The significance level for the CI, 95% CI will be .05
        :print: debug, prints out the range
        :return: Returns the lower bound and then the upperbound
        """
        Std_err = self.find_standard_error_sample()
        critical_t_value = st.t.ppf(alpha/2,self._count-1)
        self._margin_of_error = Std_err*critical_t_value
        low_bound = self._mean - Std_err*critical_t_value
        upper_bound = self._mean + Std_err*critical_t_value
        if print:
            print(f"The {percentile*100}% confidence interval for the mean is from {low_bound} to {upper_bound}")
        return low_bound, upper+bound
        
    def find_standard_error(self):
        """
        Gets the standard error if the population standard deviation is known.
        """
        return self._pop_std_dev/ (self._count**.5)

    def find_standard_error_sample(self):
        """
        Gets the standard error if the population standard deviation is unknown
        """
        return self._std_dev/(self._count**.5)
        
data = [45,47,52,59,53,55,56,58,62]
mod = QuantSample(data)
mod.summary()
