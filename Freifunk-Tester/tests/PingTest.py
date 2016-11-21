from tests.AbstractTest import AbstractTest
import re

class PingTest(AbstractTest):

    def __init__(self, serial, destination, protocol=6):
        command_string = None
        if protocol == 4:
            command_string = "ping -c4 " + destination + "\r"
        elif protocol == 6:
            command_string = "ping6 -c4 " + destination + "\r"
        else:
            raise ValueError('IP protocol version must be 4 or 6.')
        __testDescription = 'PingTest performs a standard, four packet ping test with the given destination. The benchmark it the procentual loss.'
        super(PingTest, self).__init__(serial, command_string, __testDescription)

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
