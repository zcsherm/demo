class ANOVA:
    def __init__(self,samples):
        """
        :samples: Dictionary, each key is the treatment, value is response set
        """
        self._treatments = list(samples.keys())
        self._responses = list(responses.values())
        self._groups = samples
        self._I = len(self._treatments)
        self._J = self._responses[0].get_count()
        self.find_grand_mean()
        self.find_MSTr()
        self.find_MSE()
        self.find_SSE()
        self.find_SSTr()
        self.find_SST()
        
    def find_grand_mean():
        tot = 0
        data_points = 0
        for i in range(self._I):
            tmp = self._responses[i].get_mean() * self._responses[i].get_count()
            data_points += self._responses[i].get_count()
            tot += tmp
        self._grand_mean = tot/data_points
        
    def find_MSTr():
        square_error = 0
        for i in range(self._I):
            square_error += (self._responses[i].get_mean()-self._grand_mean)**2
        square_error *= self._J
