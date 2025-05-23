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
        
    def find_grand_mean(self):
        tot = 0
        data_points = 0
        for i in range(self._I):
            tmp = self._responses[i].get_mean() * self._responses[i].get_count()
            data_points += self._responses[i].get_count()
            tot += tmp
        self._grand_mean = tot/data_points
        
    def find_MSTr(self):
        """
        Find mean squared treatment
        """
        # Presently only works for J being equal amongst samples
        square_error = 0
        for i in range(self._I):
            square_error += (self._responses[i].get_mean()-self._grand_mean)**2
        square_error *= self._J
        square_error /= (self._I-1)
        self._MSTr = square_error

    def find_MSE(self):
        square_error = 0
        for i in range(self._I):
            square_error += self._responses[i].get_standard_deviation()**2
        square_error /= self._I
        self._MSE = square_error

    def find_SST_quants(self):
        for i in range(self._I):
            var = 0
            for j in range(self._responses[i].get_count()):
                var += (self._responses[i][j] - self._grand_mean)**2
        self._SST = var
