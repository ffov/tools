from tests.AbstractTest import AbstractTest
import re

class SerialHasPrompt(AbstractTest):

    def __init__(self, serial, **kw):
        super(SerialHasPrompt, self).__init__(serial, **kw)

        self._command_string = '\x03\r'
        self._short_description = 'check for prompt'
        self._testDescription = 'Tests if the given serial console has a prompt.'
        self._benchmark_description = '0 if true, 1 if false'

    def validate(self, result):
        if self.benchmark(result) == 0:
            return True
        else:
            return False

    def benchmark(self, result):
        line = result[-1].decode('utf-8')
        prompt_pattern = re.compile(r'[$#]\s?$')
        matches = prompt_pattern.findall(line)
        if len(matches) > 0:
            return 0
        else:
            return 1
