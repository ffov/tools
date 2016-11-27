#!/usr/bin/python3.4

import serial
import re
from FfDomain import FfDomain
import libvirt
from tests import TestResult
from tests.PingTest import PingTest
from tests.HasDefaultGatewayTest import HasDefaultGatewayTest
import time

PING_COUNT=4
NAME_OF_DEBIAN_TESTMACHINE="Testdebian"
LIBVIRT_SYSTEM_PATH='qemu:///system'

testmachine = None
libvirt_connection = None

def initialize_libvirt():
    global libvirt_connection
    libvirt_connection = libvirt.open(LIBVIRT_SYSTEM_PATH)

def open_serial_to_vmname(name):
    global libvirt_connection
    global testmachine
    if libvirt_connection is None:
        initialize_libvirt()
    testmachine = FfDomain(libvirt_connection, NAME_OF_DEBIAN_TESTMACHINE)
    return testmachine.getSerial()

def execute_command(serial, command_string):
    serial.write(command_string.encode('utf-8'))
    return serial.readlines()

def standard_test(serial):
    HasDefaultGatewayTest(deb, protocol=4).execute().print_report()
    PingTest(deb, '8.8.8.8', protocol=4).execute().print_report()
    PingTest(deb, 'google.de', protocol=4).execute().print_report()
    HasDefaultGatewayTest(deb).execute().print_report()
    PingTest(deb, '2a00:1450:4001:804::2003').execute().print_report()
    PingTest(deb, 'google.de').execute().print_report()

def tests_for_all_networks():
    global testmachine
    if libvirt_connection is None:
        initialize_libvirt()
    for net in sorted(libvirt_connection.listNetworks()):
        if "Clientnetz" in net:
            print ("Bearbeite " + net)
            gluonname = net.replace("Clientnetz-", "Gluon-", 1)
            gluon = libvirt_connection.lookupByName(gluonname)
            if not gluon.isActive():
                print(gluonname + " läuft nicht. Wird nun gestartet. Warte 120 Sekunden.")
                gluon.create()    
                time.sleep(120)

            if gluon.isActive():
                testmachine.setNetwork(net)
                testmachine.restartNetwork()
                standard_test(testmachine.getSerial())
 


deb = open_serial_to_vmname(NAME_OF_DEBIAN_TESTMACHINE)
#standard_test(deb)
tests_for_all_networks()
