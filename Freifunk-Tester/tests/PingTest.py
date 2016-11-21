from tests import AbstractTest

class PingTest(AbstractTest):
    __testDescription = 'PingTest performs a standard, four packet ping test with the given destination. The benchmark it the procentual loss.'

    def __init__(self, serial, destination, protocol=6):
        self.__serial = serial
        if protocol = 4:
            self.__command_string = "ping -c4 " + destination
        elif protocol = 6::
            self.__command_string = "ping6 -c4 " + destination
        else:
            raise ValueError('IP protocol version must be 4 or 6.')

    def validate(self, result):
        if benchmark(result) == 0:
            return True
        else
            return False

    def benchmark(self, result):
        for byteline in outputlines:
            line = byteline.decode('utf-8')
            if "received" in line:
                packet_loss = re.compile(r", \d+% packet loss")
                result = packet_loss.findall(line)
                return result[0][2:result[0].index('%')]
        return -1
