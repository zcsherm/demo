# Class representing a singles sample 
from math import floor
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
        self._labesl = list(labels)
        self._count = len(data_set)

    def add_sample(self,data_point,label=None):
        self._samples.append(data_point)
        self._count += 1
        if label is None:
            label = len(self._labels)
        self._label.append(label)


class ProportionSample(Sample):
    def __init__(self,data_set,labels=None,positive_case=None):
        super().__init__(data_set,labels)
        self._positive_case = positive_case
        self._positives = self.find_positives(positive_case)
        self._proportion = self.find_proportion()
        
    def find_positives(self, positive_case):
        total_positive = 0
        for i in range(self._count):
            if self._samples[i] == positive_case:
                total_positive += 1
        return total_positives
    
    def find_proportion(self):
        return self._positives/self._count
        
class QuantSample(Sample):
    def __init__(self,data_set,labels=None):
        super().__init__(data_set,labels)
        self._mean = self.find_mean()
        self._median = self.find_median()
        self._skew = self.find_skew_amount()
        self._std_dev = self.find_std_dev()
        self._variance = self.find_variance()
        self._IQR_range = self.find_IQR()
        
    def find_mean(self):
        total = 0
        for i in range(self._count):
            total += self._samples[i]
        return total/self._count

    def find_median(self):
        if self._count % 2 == 0:
            print((self._count/2))
            median = (self._samples[(self._count-1)//2]+self._samples[self._count//2])/2
        else:
            
            median = self._samples[self._count//2]
        return median
        
    def find_skew_amount(self):
        return self._mean-self._median

    def find_IQR(self):
        # get Q1
        if self._count % 2 ==0:
            Q2 = ((self._count/2+(self._count+2)//2)/2)
            print(Q2)
            if floor(Q2) % 2 == 0:
                Q2 = int(Q2)
                Q1 = (self._samples[(Q2//2)-1] + self._samples[(Q2+2)//2-1])/2
                print(f"hey {self._samples[((3*Q2)//2)-1]} and {self._samples[(3*Q2+2)//2-1]}")
                Q3 = (self._samples[((3*Q2)//2)-1] + self._samples[(3*Q2+2)//2-1])/2
            else:
                Q2 = int(Q2)
                Q1 =self._samples[Q2//2]
                Q3 =self._samples[int(3*(Q2//2)+1)]
        else: 
            Q2 = int((self._count+1)//2)
            print(Q2)
            if Q2 % 2 ==0:
                Q1 = self._samples[(Q2//2)]
                Q3 = self._samples[(3*Q2)//2+1]
            else:
                Q1 = (self._samples[int((Q2)//2-1)]+self._samples[int(Q2)//2])/2
                Q3 = (self._samples[int((3*(Q2-1))//2)]+self._samples[int(3*Q2)//2])/2
        self._Q1 = Q1
        self._Q3 = Q3
        return Q3-Q1
            
        
        

    def find_std_dev(self):
        sum = 0
        for i in range(self._count):
            sum += (self._samples[i]-self._mean)**2
        sum /= self._count
        return sum**.5

    def find_variance(self):
        return self._std_dev**2

    
