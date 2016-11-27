import libvirt
import xml.etree.ElementTree as ET
import serial

SERIAL_TIMEOUT=2

class FfDomain(libvirt.virDomain):
    def __init__(self, virConnect, vmName):
        self._domain = virConnect.lookupByName(vmName)
        self._serial = self.__setupSerial()

    def __del__(self):
        self._domain.__del__()
        self._serial.__del__()
        
    def __setupSerial(self):
        domain_xml = self._domain.XMLDesc()
        xml_root = ET.fromstring(domain_xml) 
        devices = xml_root.find('devices')
        console = devices.find('console')
        serialPath = console.get('tty')
        return serial.Serial(serialPath, timeout=SERIAL_TIMEOUT)

    def getSerial(self):
        return self._serial
