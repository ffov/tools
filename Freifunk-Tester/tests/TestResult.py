class TestResult(object):
    def __init__(self, passed, benchmark_number, testDescription, rawOutput, optionalStuff=None):
        self.__passed = passed
        self.__benchmark_number = benchmark_number
        self.__testDescription = testDescription
        self.__rawOutput = rawOutput
        self.__optionalStuff = optionalStuff 

    def passed(self):
        return self.__passed

    def benchmark(self):
        return self.__benchmark_number

    def testDescription(self):
        return self.__testDescription

    def getRawOutput(self):
        return self.__rawOutput

    def getOptionalStuff(self):
        return self.__optionalStuff
