#!/bin/python

import serial
import re
from FfDomain import FfDomain
import libvirt

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

def parse_ping_loss(outputlines):
    for byteline in outputlines:
        line = byteline.decode('utf-8')
        if "received" in line:
            packet_loss = re.compile(r", \d+% packet loss")
            result = packet_loss.findall(line)
            return result[0][2:result[0].index('%')]
    return -1

def perform_ping_v4_test(serial, destination):
    command = "ping -c" + str(PING_COUNT) + " " + destination + '\r'
    output = execute_command(serial, command)
    return parse_ping_loss(output)
    
def perform_ping_v6_test(serial, destination):
    command = "ping6 -c" + str(PING_COUNT) + " " + destination + '\r'
    output = execute_command(serial, command)
    return parse_ping_loss(output)

def get_default_gateway_v4(serial):
    command = "ip r\r"
    output = execute_command(serial, command)
    return parse_default_gateway(output)

def get_default_gateway_v6(serial):
    command = "ip -6 r\r"
    output = execute_command(serial, command)
    return parse_default_gateway(output)

def parse_default_gateway(outputlines):
    for byteline in outputlines:
        line = byteline.decode('utf-8')
        if "default" in line:
            line = line[12:]
            return line[:line.index(' ')]

def standard_test(serial):
    print ("V4 default gateway: " + get_default_gateway_v4(serial))
    print ("V4 loss to 8.8.8.8: " + str(perform_ping_v4_test(serial, "8.8.8.8")) + "%")
    print ("V4 loss to google.de: " + str(perform_ping_v4_test(serial, "google.de")) + "%")
    print ("V6 default gateway: " + get_default_gateway_v6(serial))
    print ("V6 loss to google.de: " + str(perform_ping_v6_test(serial, "google.de")) + "%")
    print ("V6 loss to 2a00:1450:4001:804::2003: " + str(perform_ping_v6_test(serial, "2a00:1450:4001:804::2003")) + "%")

deb = open_serial_to_vmname(NAME_OF_DEBIAN_TESTMACHINE)
standard_test(deb)
