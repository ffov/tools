from tests.AbstractTest import AbstractTest
import re

class HasDefaultGatewayTest(AbstractTest):

    def __init__(self, serial, protocol=6, **kw):
        super(HasDefaultGatewayTest, self).__init__(serial, **kw)
        if protocol == 4:
            self._command_string = "ip r s\r"
            self._short_description = 'Has IPv4 default gateway'
        elif protocol == 6:
            self._command_string = "ip -6 r s\r"
            self._short_description = 'Has IPv6 default gateway'
        else:
            raise ValueError('IP protocol version must be 4 or 6.')

        self._testDescription = "HasDefaultGatewayTest tests weather there is a default gateway in the kernel's routing table"
        self._benchmark_description = 'default gateway'

    def validate(self, result):
        if self.benchmark(result) != 0:
            return True
        else:
            return False

    def benchmark(self, result):
        try:
            for byteline in result:
                line = byteline.decode('utf-8')
                if "default" in line:
                    line = line[12:]
                    return line[:line.index(' ')]

            return int(0)
        except:
            return int(0)
