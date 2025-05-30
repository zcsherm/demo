from sample import *
from model import *
import scipy.stats as st
class experiment:
    # Represents a set of treatments and responses for an experiment. Can perform multi t and anova analysis
    def __init__(self, samples, treatments, dependence = False):
        self._groups = {}
        # For each sample set, we set them up as a dictionary (ie {"students":samp1, "Teachers":samp2..}
        for i in range(len(samples)):
            self._groups[treatments[i]] = samples[i]
        # Assume that all samples have the same number of samples
        self._sample_counts= samples[0].get_count()
        self._samples = samples
        self._treatments = treatments
        self._dependence = dependence
        
    def matched_pairs_t(self,claim,alpha,tails=2,print=False):
        """
        Perform a matched t pairs test.
        """
        # Data must be dependent and have 2 samples
        if self._dependence == False:
            return None
        if len(self._treatments) != 2:
            return None
        # find the vector of all differences and d-hat, the average difference
        differences = []
        for i in range(self._sample_counts):
            differences.append(self._samples[0].get_measurement(i)-self._samples[1].get_measurement(i))
        d_hat = sum(differences)/len(differences)
        # Get the standard deviation of differences
        std_dev_diff = 0
        for i in range(len(differences)):
            std_dev_diff += (differences[i]-d_hat)**2
        std_dev_diff /= (len(differences)-1)
        # get the standard error
        std_err_diff = std_dev_diff/(self._sample_counts**.5)
        t_stat = (d_hat-claim)/std_err_diff
        margin_of_error = st.t.ppf(alpha/2,len(differences)-1)*std_err_diff
        lower_bound = d_hat - margin_of_error
        upper_bound = d_hat + margin_of_error
        p_value = (1-st.t.cdf(t_stat,self._count-1))*tails
        if print:
            print(f"The probability that the 2 samples have a difference of {d_hat}, when the proposed difference is {claim}, is {p_value}, for a {tails} tailed t-test.")
            if p_value < alpha:
                print(f"The null hypothesis of {claim} is rejected at a significance level of {alpha}, from a t-stat of {t-stat}")
            print(f"The {(1-alpha)*100}% confidence interval for the mean is from {low_bound} to {upper_bound} with a margin of error of {margin_of_error}")
        return p_value

    def two_sample_t_test(self,claim,alpha,tails=2,print=False):
        """
        Perform 2 sample t test and confidence interval
        """
        if self._dependence == True:
            return None
        if len(self._treatments) != 2:
            return None
        # first get standard error
        std_error = (self._samples[0].get_standard_deviation()/self._samples[0].get_count()+self._samples[1].get_standard_deviation()/self._samples[1].get_count())**.5
        # get t test stat
        diff = self._samples[0].get_mean()-self._samples[1].get_mean()
        t_stat = (diff-claim)/std_error
        deg_of_freedom = self.satterthwaite(self._samples[0].get_standard_deviation(),self._samples[1].get_standard_deviation(),self._samples[0].get_count(),self._samples[1].get_count())
        margin_of_error = st.t.ppf(alpha/2,deg_of_freedom) * std_error
        lower_bound = diff - margin_of_error
        upper_bound = diff + margin_of_error
        p_value = (1-st.t.cdf(t_stat,deg_of_freedom))*tails
        if print:
            print(f"The probability that the 2 samples have a difference of {diff}, when the proposed difference is {claim}, is {p_value}, for a {tails} tailed t-test.")
            if p_value < alpha:
                print(f"The null hypothesis of {claim} is rejected at a significance level of {alpha}, from a t-stat of {t-stat}")
            print(f"The {(1-alpha)*100}% confidence interval for the mean is from {low_bound} to {upper_bound} with a margin of error of {margin_of_error}")
        return p_value

    def satterthwaite(self,s1,s2,n1,n2):
        num = (s1**2/n1+s2**2/n2)**2
        denom = ((s1**2/n1)**2/(n1-1))+((s2**2/n2)**2/(n2-1))
        return floor(num/denom)
            
    def single_factor_ANOVA(self):
        """
        Perform a single factor ANOVA analysis
        """
        # Get MSTr
        # Get MSE
        # Get SST
        # Get SSTR
        # Get SSE
