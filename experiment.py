from sample import *
class experiment:
    # Represents a set of treatments and responses for an experiment. Can perform multi t and anova analysis
    def __init__(self, samples, treatments, dependence = False):
        self._groups = {}
        for i in range(len(samples)):
            self._groups[treatments[i]] = samples[i]
        self._sample_counts= samples[0].get_count()
        self._samples = samples
        self._treatments = treatments
        self.dependence = dependence
        
    def matched_pairs_t(self):
        if self._dependence == False:
            return None
        if len(self._treatments) != 2:
            return None
        differences = []
        for i in range(self._sample_counts):
            differences.append(self._samples[0].get_measurement(i)-self._samples[1].get_measurement(i))
        d_hat = sum(differences)/len(differences)
        
        std_dev_diff = 0
        for i in range(len(differences)):
            std_dev_diff += (differences[i]-d_hat)**2
        std_dev_diff /= (self._sample_counts-1)

        std_err_diff = std_dev_diff/(self._sample_counts**.5)
    
                
            
