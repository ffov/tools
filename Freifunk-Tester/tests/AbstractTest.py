from abc import ABC, abstractmethod
from tests import TestResult

class AbstractTest(ABC):
    __testDescription = 'This is the abstract test class without any description.'

    def __init__(self, serial):
        self.__serial = serial
        pass

    def _runCommand(self):
        __serial.write(__command_string.encode('utf-8'))
        return serial.readlines()

    def execute(self):
        rawOutput = _runCommand()
        return TestResult(validate(rawOutput), benchmark(rawOutput), __testDescription, rawOutput)

    @abstractmethod
    def validate(self, result):
        pass
        
    @abstractmethod
    def benchmark(self, result):
        pass

    def getDescription(self):
        return __testDescription

