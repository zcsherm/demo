import scipy.stats as st'
from itertools import combinations
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
        self._v1 = self._I-1
        self._v2= self._I * (self._J-1)
        self.find_grand_mean()
        self.find_MSTr()
        self.find_MSE()
        self.find_SSE_quants()
        if !self._validate_error_quantities():
            print("There was an issue with the error values")
        # Get F stat
        self.find_F_test()
        self.find_p_value()
    
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
            sstr = 0
            sse = 0
            for j in range(self._responses[i].get_count()):
                var += (self._responses[i][j] - self._grand_mean)**2
                sstr += (self._responses[i].get_mean()-self._grand_mean)**2
                sse += (self._responses[i][j]-self._responses[i].get_mean())**2
        self._SST = var
        self._SSTr = sstr
        self._SSE = sse

    def validate_error_quantities(self):
        passed = True
        # case 1: MSTr = SStr/I-1
        if self._MSTr != self._SSTr/(self._I-1):
            print(f"MSTr: {self._MSTr} DOES NOT EQUAL SSTr/({self._I-1}):{self._SSTr}/{self._I}-1: {self._SSTr/(self._I-1)}")
            passed = False
        # Case 2: MSE = SSE/(I(J-1))
        if self._MSE != self._SSE/(self._I*(self._J-1)):
            print(f"MSE: {self._MSE} DOES NOT EQUAL SSE/({self._I*(self._J-1)}):{self._SSE}/{self._I}({self._J}-1): {self._SSE/(self._I*(self._J-1)}")
            passed = False
        # Case 3: SST = SSE + SSTr
        if self._SST != self._SSE + self._SSTr:
            print(f"SST: {self._SST} DOES NOT EQUAL SSE/SSTR: {self._SSE}/{self._SSTr}: {self._SSE/self._SSTr}")
            passed = False
        return passed

    def find_F_test(self):
        self._F_stat = self._MSTr/self._MSE

    def find_p_value(self):
        # get the pf
        cumulative = st.f.cdf(self._F_stat, self._v1, self._v2)
        self._p_value = 1-cumulative

    def tukey_HSD(self, confidence_level):
        combos = combinations(self._treatments,2)
        self._family_comps = {}
        for i in range(len(combos)):
            # Get the confidence interval for each pair of treatments
            mean_1 = self_treatments[combos[i][0]].get_mean()
            mean_2 = self_treatments[combos[i][1]].get_mean()
            margin_of_error = st.studentized_range.ppf(1-confidence_level,self._v1,self._v2) * ((self._MSE/self._J)**.5)
            self._family_comps[combos[i]] =((mean1-mean2)-margin_of_error,(mean1-mean2)+margin_of_error,(mean1_mean2))

    def print_tukey_HSD(self):
        keys = list(self._family_comps.keys()
        for i in range(len(keys)):
            print(f"{keys[i][0]} and {keys[i][1]} --- diff: {self._family_comps[keys[i]][2]} --- low bound:{self._family_comps[keys[i]][0]} --- high bound: {self._family_comps[keys[i]][1]}"
