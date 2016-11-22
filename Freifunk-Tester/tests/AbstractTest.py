from abc import ABC, abstractmethod
from tests.TestResult import TestResult

class AbstractTest(ABC):

    def __init__(self, serial):
        self._serial = serial
        self._command_string = "echo 'This is a test command.'"
        self.__testDescription = "This is the AbstractTest class."

    def _runCommand(self):
        self._serial.write(self._command_string.encode('utf-8'))
        return self._serial.readlines()

    def execute(self):
        rawOutput = self._runCommand()
        return TestResult(self.validate(rawOutput), self.benchmark(rawOutput), self.__testDescription, rawOutput)

    @abstractmethod
    def validate(self, result):
        pass
        
    @abstractmethod
    def benchmark(self, result):
        pass

    def getDescription(self):
        return __testDescription

