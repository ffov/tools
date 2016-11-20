import libvirt
import xml.etree.ElementTree as ET
import serial

SERIAL_TIMEOUT=2

class FfDomain(libvirt.virDomain):
    def __init__(self, virConnect, vmName):
        self._domain = virConnect.lookupByName(vmName)

    def __del__(self):
        self._domain.__del__()
        
    def getSerial(self):
        domain_xml = self._domain.XMLDesc()
        xml_root = ET.fromstring(domain_xml) 
        devices = xml_root.find('devices')
        console = devices.find('console')
        serialPath = console.get('tty')
        return serial.Serial(serialPath, timeout=SERIAL_TIMEOUT)
