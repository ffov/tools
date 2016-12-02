#!/usr/bin/python3.4

import serial
import re
from FfDomain import FfDomain
import libvirt
from tests import TestResult
from tests.PingTest import PingTest
from tests.HasDefaultGatewayTest import HasDefaultGatewayTest
import time
import os

PING_COUNT=4
NAME_OF_DEBIAN_TESTMACHINE="Testdebian"
LIBVIRT_SYSTEM_PATH='qemu:///system'

testmachine = None
libvirt_connection = None
one_failed = False

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

def report_if_failed(result):
    global one_failed
    if not result.passed():
        curl_command = '''curl -d '{"color":"red","message":"''' + result.report().replace('\r', ' ').replace('\n', ' ').replace('"', '\\"').replace("'", "\\'") + '''","notify":false,"message_format":"text"}' -H 'Content-Type: application/json' https://hc.infrastruktur.ms/v2/room/13/notification?auth_token=HeoSTcIvLsm8MXD4WefcEVfbXKXKemLtTFxbWoxj'''
        os.system(curl_command)
        one_failed = True

def run_test(test):
    result = test.execute()
    result.print_report()
    report_if_failed(result)

def report_if_none_failed():
    global one_failed
    if not one_failed:
        curl_command = """curl -d '{"color":"green","message":"Testzyklus komplett, alles funktioniert, wie es soll.","notify":false,"message_format":"text"}' -H 'Content-Type: application/json' https://hc.infrastruktur.ms/v2/room/13/notification?auth_token=HeoSTcIvLsm8MXD4WefcEVfbXKXKemLtTFxbWoxj"""
        os.system(curl_command)

def standard_test(serial, domain="unknown", gateway="random"):
    run_test(HasDefaultGatewayTest(deb, protocol=4, domain=domain, gateway=gateway))
    run_test(PingTest(deb, '8.8.8.8', protocol=4, domain=domain, gateway=gateway))
    run_test(PingTest(deb, 'google.de', protocol=4, domain=domain, gateway=gateway))
    run_test(HasDefaultGatewayTest(deb, domain=domain, gateway=gateway))
    run_test(PingTest(deb, '2a00:1450:4001:804::2003', domain=domain, gateway=gateway))
    run_test(PingTest(deb, 'google.de', domain=domain, gateway=gateway))

def tests_for_all_networks():
    global testmachine
    if libvirt_connection is None:
        initialize_libvirt()
    for net in sorted(libvirt_connection.listNetworks()):
        if "Clientnetz" in net:
            print ("Bearbeite " + net)
            gluonname = net.replace("Clientnetz-", "Gluon-", 1)
            domain = net.replace("Clientnetz-", "", 1)
            gluon = libvirt_connection.lookupByName(gluonname)
            if not gluon.isActive():
                print(gluonname + " läuft nicht. Wird nun gestartet. Warte 120 Sekunden.")
                gluon.create()    
                time.sleep(120)

            if gluon.isActive():
                testmachine.setNetwork(net)
                testmachine.restartNetwork()
                time.sleep(60)
                standard_test(testmachine.getSerial(), domain=domain)

            gluon.destroy()
 


deb = open_serial_to_vmname(NAME_OF_DEBIAN_TESTMACHINE)
#standard_test(deb)
while (True):
    tests_for_all_networks()
    report_if_none_failed()
    one_failed = False
