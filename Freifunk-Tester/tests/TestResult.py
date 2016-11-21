class TestResult(object):
    def __init__(self, passed, benchmark_number, testDescription, rawOutput, optionalStuff=None):
        self.__passed = passed
        self.__benchmark_number = benchmark_number
        self.__testDescription = testDescription
        self.__rawOutput = rawOutput
        self.__optionalStuff = optionalStuff 

    def passed(self):
        return __passed

    def benchmark(self):
        return __benchmark_number

    def testDescription(self):
        return __testDescription

    def getRawOutput(self):
        return __rawOutput

    def getOptionalStuff(self):
        return __optionalStuff
