from tests.AbstractTest import AbstractTest
import re

class PingTest(AbstractTest):

    def __init__(self, serial, destination, protocol=6):
        super(PingTest, self).__init__(serial)
        if protocol == 4:
            self._command_string = "ping -c4 " + destination + "\r"
            self._short_description = 'IPv4 ping test to ' + destination
        elif protocol == 6:
            self._command_string = "ping6 -c4 " + destination + "\r"
            self._short_description = 'IPv6 ping test to ' + destination
        else:
            raise ValueError('IP protocol version must be 4 or 6.')

        self._testDescription = 'PingTest performs a standard, four packet ping test with the given destination. The benchmark is the procentual loss.'
        self._benchmark_description = 'procental loss of packets'

    def validate(self, result):
        if self.benchmark(result) == 0:
            return True
        else:
            return False

    def benchmark(self, result):
        try:
            for byteline in result:
                line = byteline.decode('utf-8')
                if "received" in line:
                    packet_loss = re.compile(r", \d+% packet loss")
                    result = packet_loss.findall(line)
                    return int(result[0][2:result[0].index('%')])
        except:
            return int(-1)
