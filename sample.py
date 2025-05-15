# Class representing a singles sample 
from math import floor
import scipy.stats as st
# Now that I'm just gonna use scipy, might as well change z score table to a function
CONFIDENCE_Z_SCORES = {.9:1.645,
                      .95:1.96,
                      .99:2.576}
class Sample:
    def __init__(self,data_set, labels=None):
        if labels is None:
            labels = []
            for i in range(len(data_set)):
                labels.append(i+1)
        zipped = zip(data_set, labels)
        zipped = sorted(zipped)
        samples, labels = zip(*zipped)
        self._samples = list(samples)
        self._labels = list(labels)
        self._count = len(data_set)

    def add_sample(self,data_point,label=None):
        # Doesn't preserve sorted order and causes issues
        self._samples.append(data_point)
        self._count += 1
        if label is None:
            label = len(self._labels)
        self._label.append(label)

    def get_count(self):
        return self._count

    def get_measurement(self,index):
        return self._samples[index]
        
class ProportionSample(Sample):
    def __init__(self,data_set,labels=None,positive_case=None):
        super().__init__(data_set,labels)
        self._positive_case = positive_case
        self._positives = self.find_positives(positive_case)
        self._proportion = self.find_proportion()
        self._std_dev = self.find_standard_deviation()
        
    def find_positives(self, positive_case):
        total_positive = 0
        for i in range(self._count):
            if self._samples[i] == positive_case:
                total_positive += 1
        return total_positives

    def find_standard_deviation(self):
        return ((self._proportion*(1-self._proportion))/n)**.5
        
    def find_proportion(self):
        return self._positives/self._count

    def confidence_interval(self, percentile, print=False):
         # Get the confidence interval for a true mean, when population std dev is known
        if percentile > 1:
            percentile = percentile / 100
        if percentile not in CONFIDENCE_Z_SCORES or self._pop_std_dev is None:
            return None
        low_bound = self._proportion - (self.find_sample_error() * CONFIDENCE_Z_SCORES[percentile])
        upper_bound = self._proportion + (self.find_sample_error() * CONFIDENCE_Z_SCORES[percentile])
        if print:
            print(f"The (percentile*100)% confidence interval for the population proportion is from {low_bound} to {upper_bound}")
        return low_bound, upper_bound

    def perform_z_test(self, claim, alpha, tails=2, print=False, CI=.5):
        # Fix bug for finding left tailed test
        z_stat = ((self._proportion - claim)/((claim*(1-claim))/self._count)**.5)
        p_value = (1- st.norm.cdf(z_stat)) * tails
        if print:
            print(f"The probability that a sample would have a mean of {self._proportion}, when the true mean is {claim}, is {p_value}, for a {tails} tailed test.")
            if p_value < alpha:
                print(f"The null hypothesis of {claim} is rejected at a significance level of {alpha}, from a z-stat of {z-stat}")
            self.confidence_interval(CI, True)
        return p_value
        
    def find_sample_error(self):
        return ((self._proportion * (1-self._proportion))/n)**.5

    # Add in a summary function

class QuantSample(Sample):
    # Handles a sample of quantatitive variables
    def __init__(self,data_set,labels=None):
        super().__init__(data_set,labels)
        self._mean = self.find_mean()
        self._median = self.find_median()
        self._skew = self.find_skew_amount()
        self._std_dev = self.find_std_dev()
        self._variance = self.find_variance()
        self._IQR_range = self.find_IQR()
        self._low_outliers, self._high_outliers = self.find_outliers() 
        self._pop_std_dev = None
        
    def find_mean(self):
        # Get the mean by summing all values, divide by count
        total = 0
        for i in range(self._count):
            total += self._samples[i]
        return total/self._count

    def find_median(self):
        # If there is an even number of elements, get an average of the 2 middle entries
        if self._count % 2 == 0:
            median = (self._samples[(self._count-1)//2]+self._samples[self._count//2])/2
        # If there is an odd number of elements, get the precise middle element
        else:
            median = self._samples[self._count//2]
        return median
        
    def find_skew_amount(self):
        # Get how much the mean is pulled from the median
        return self._mean-self._median

    def find_IQR(self):
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
        # Find the average squared error of each sample - Uses std dev of pop formula
        sum = 0
        for i in range(self._count):
            sum += (self._samples[i]-self._mean)**2
        sum /= self._count
        return sum**.5

    def find_variance(self):
        return self._std_dev**2

    def find_outliers(self):
        low_outliers = []
        high_outliers = []
        lowcutoff = self._Q1-(self._IQR_range *1.5)
        highcutoff = self._Q3 + (self._IQR_range * 1.5)
        for i in range(self._count):
            if self._samples[i]<lowcutoff:
                low_outliers.append(self._samples[i])
            if self._samples[i]>highcutoff:
                high_outliers.append(self._samples[i])
        return low_outliers, high_outliers

    def set_population_std_dev(self,std_dev):
        self._pop_std_dev = std_dev
        
    
    def summary(self):
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
        # Get the confidence interval for a true mean, when population std dev is known
        if percentile > 1:
            percentile = percentile / 100
        if percentile not in CONFIDENCE_Z_SCORES or self._pop_std_dev is None:
            return None
        sigma_hat = self._pop_std_dev/(self._count ** self._count)
        low_bound = self._mean - (sigma_hat * CONFIDENCE_Z_SCORES[percentile])
        upper_bound = self._mean + (sigma_hat * CONFIDENCE_Z_SCORES[percentile])
        if print:
            print(f"The {percentile*100}% confidence interval for the mean is from {low_bound} to {upper_bound}")
        return low_bound, upper_bound

    def perform_z_test(self, claim, alpha, tails=2, print=False, CI=.95):
        # If populations standard deviation is known
        if self._pop_std_dev is None:
            return None
        if alpha > 1:
            alpha /= 100
        z_stat = (self._mean - claim) / (self._pop_std_dev/(self._count**.5))
        p_value = (1- st.norm.cdf(z_stat)) * tails
        if print:
            print(f"The probability that a sample would have a mean of {self._mean}, when the true mean is {claim}, is {p_value}, for a {tails} tailed z-test.")
            if p_value < alpha:
                print(f"The null hypothesis of {claim} is rejected at a significance level of {alpha}, from a z-stat of {z-stat}")
            self.confidence_interval(CI, True)
        return p_value

    def perform_t_test(self,claim,alpha,tails=2,print=False,CI=.95):
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
        Std_err = self.find_standard_error_sample()
        critical_t_value = st.t.ppf(alpha/2,self._count-1)
        low_bound = self._mean - Std_err*critical_t_value
        upper_bound = self._mean + Std_err*critical_t_value
        if print:
            print(f"The {percentile*100}% confidence interval for the mean is from {low_bound} to {upper_bound}")
        return low_bound, upper+bound
        
    def find_standard_error(self):
        return self._pop_std_dev/ (self._count**.5)

    def find_standard_error_sample(self):
        return self._std_dev/(self._count**.5)
data = [45,47,52,59,53,55,56,58,62]
mod = QuantSample(data)
mod.summary()
