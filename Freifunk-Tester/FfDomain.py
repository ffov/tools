import libvirt
import xml.etree.ElementTree as ET
import serial
import sys

from urllib import request 
from urllib.request import urlretrieve

SERIAL_TIMEOUT=5

GLUON_URL="http://firmware.freifunk-muensterland.org/domaene01/stable/sysupgrade/gluon-ffmsd01-v2016.2.1%2B2.1.0-x86-64-sysupgrade.img.gz"

class FfDomain():
    def __init__(self, virConnect, vmName, domID=None):
        self.domID = domID
        try:
           self.domain = virConnect.lookupByName(vmName)
           self.serial = serial.Serial(self.__getSerialPath(), timeout=SERIAL_TIMEOUT)
        except:
           print("VM wurde nicht gefunden.")
           self.__downloadGluon()


    def __downloadGluon(self):
        url = GLUON_URL.replace("01", "{0:0>2}".format(self.domID), 2)
        print(url)
        urlretrieve(url)
        sys.exit(2)
           


#    def __del__(self):
#        self.serial.__del__()
#        self.domain.__del__()
        
    def __getSerialPath(self):
        domain_xml = self.domain.XMLDesc()
        xml_root = ET.fromstring(domain_xml) 
        devices = xml_root.find('devices')
        console = devices.find('console')
        serialPath = console.get('tty')
        return serialPath

    def getSerial(self):
        return self.serial

    def setNetwork(self, network_name):
        domain_xml = self.domain.XMLDesc()
        xml_root = ET.fromstring(domain_xml) 
        devices = xml_root.find('devices')
        interface = devices.find('interface')
        network = interface.find('source')
        network.set("network", network_name)
        changed_xml = ET.tostring(interface, method='xml').decode('utf-8')
        self.domain.updateDeviceFlags(changed_xml) 

    def execute_command(self, command_string):
        self.serial.write(command_string.encode('utf-8'))
        return self.serial.readlines()

    def restartNetwork(self):
        self.execute_command("ifdown eth0; ifup eth0\r")

    def renew_dhcp_v4(self):
        print(self.execute_command("dhclient eth0\r"))

