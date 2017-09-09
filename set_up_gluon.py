#!/usr/bin/python3

import sys
import urllib.request
import urllib.parse
import gzip
import os
import libvirt

DEFAULT_DESTINATION_PATH="/var/lib/libvirt/images"

LIBVIRT_SYSTEM_PATH='qemu:///system'

name = None
domain = None
gluon_domain = None
libvirt_connection = None

TEMPLATE ="""<domain type='kvm'>
  <name>$vmName</name>
  <memory unit='KiB'>65536</memory>
  <currentMemory unit='KiB'>65536</currentMemory>
  <vcpu placement='static'>1</vcpu>
  <resource>
    <partition>/machine</partition>
  </resource>
  <os>
    <type arch='x86_64' machine='pc-i440fx-2.1'>hvm</type>
    <boot dev='hd'/>
  </os>
  <features>
    <acpi/>
    <apic/>
    <pae/>
  </features>
  <cpu mode='custom' match='exact'>
    <model fallback='allow'>SandyBridge</model>
  </cpu>
  <clock offset='utc'>
    <timer name='rtc' tickpolicy='catchup'/>
    <timer name='pit' tickpolicy='delay'/>
    <timer name='hpet' present='no'/>
  </clock>
  <on_poweroff>destroy</on_poweroff>
  <on_reboot>restart</on_reboot>
  <on_crash>restart</on_crash>
  <pm>
    <suspend-to-mem enabled='no'/>
    <suspend-to-disk enabled='no'/>
  </pm>
  <devices>
    <emulator>/usr/bin/kvm</emulator>
    <disk type='file' device='disk'>
      <driver name='qemu' type='raw'/>
      <source file='$imagePath/$vmIMG'/>
      <backingStore/>
      <target dev='vda' bus='virtio'/>
      <alias name='virtio-disk0'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x08' function='0x0'/>
    </disk>
    <interface type='network'>
      <source network='$clientnetz'/>
      <model type='virtio'/>
      <alias name='net0'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>
    </interface>
    <interface type='network'>
      <source network='default'/>
      <model type='virtio'/>
      <alias name='net1'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x04' function='0x0'/>
    </interface>
    <serial type='pty'>
      <target port='0'/>
      <alias name='serial0'/>
    </serial>
    <console type='pty' >
      <target type='serial' port='0'/>
      <alias name='serial0'/>
    </console>
    <channel type='spicevmc'>
      <target type='virtio' name='com.redhat.spice.0'/>
      <alias name='channel0'/>
      <address type='virtio-serial' controller='0' bus='0' port='1'/>
    </channel>
    <input type='mouse' bus='ps2'/>
    <input type='keyboard' bus='ps2'/>
    <graphics type='spice' port='5912' autoport='yes' listen='127.0.0.1'>
      <listen type='address' address='127.0.0.1'/>
    </graphics>
    <sound model='ich6'>
      <alias name='sound0'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x05' function='0x0'/>
    </sound>
    <video>
      <model type='vmvga' vram='9216' heads='1'/>
      <alias name='video0'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x02' function='0x0'/>
    </video>
    <redirdev bus='usb' type='spicevmc'>
      <alias name='redir0'/>
    </redirdev>
    <redirdev bus='usb' type='spicevmc'>
      <alias name='redir1'/>
    </redirdev>
     <controller type='usb' index='0' model='ich9-ehci1'>
       <address type='pci' domain='0x0000' bus='0x00' slot='0x06' function='0x7'/>
     </controller>
     <controller type='usb' index='0' model='ich9-uhci1'>
       <master startport='0'/>
       <address type='pci' domain='0x0000' bus='0x00' slot='0x06' function='0x0' multifunction='on'/>
     </controller>
     <controller type='usb' index='0' model='ich9-uhci2'>
       <master startport='2'/>
       <address type='pci' domain='0x0000' bus='0x00' slot='0x06' function='0x1'/>
     </controller>
     <controller type='usb' index='0' model='ich9-uhci3'>
       <master startport='4'/>
       <address type='pci' domain='0x0000' bus='0x00' slot='0x06' function='0x2'/>
     </controller>
     <controller type='pci' index='0' model='pci-root'/>
    <controller type='virtio-serial' index='0'>
      <alias name='virtio-serial0'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x07' function='0x0'/>
    </controller>
    <memballoon model='virtio'>
      <alias name='balloon0'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x09' function='0x0'/>
    </memballoon>
  </devices>
</domain>"""

TEMPLATE_NETZ="""<network connections='1'>
  <name>$clientnetz</name>
  <bridge stp='on' delay='0'/>
</network>"""

def download_image_file_and_unzip_it(link):
   global name
   splits = sys.argv[1].split('/')
   n = len(splits)
   name = urllib.parse.unquote(splits[n-1])
   resultFilePath, responseHeaders = urllib.request.urlretrieve(sys.argv[1], name)

   inF = gzip.open(name, 'rb')
   outF = open(DEFAULT_DESTINATION_PATH + '/' + name.replace(".gz", ""), 'wb')
   outF.write( inF.read() )
   inF.close()
   outF.close()
   os.remove(name)

def open_libvirt_connection():
    global libvirt_connection
    libvirt_connection = libvirt.open(LIBVIRT_SYSTEM_PATH) 

def install_vm():
    global TEMPLATE
    global name, domain, gluon_domain
    global libvirt_connection
    xml = TEMPLATE.replace('$vmName', domain).replace('$imagePath', DEFAULT_DESTINATION_PATH).replace('$vmIMG', name.replace(".gz","")).replace('$clientnetz', 'Clientnetz-'+domain)
    gluon_domain = libvirt_connection.defineXML(xml)
    gluon_domain.create()

def extract_domain():
    global name, domain   
    domain = name.split("-")[1]
    print(domain)

def setup_clientnetz():
    global domain
    global TEMPLATE_NETZ
    global libvirt_connection
    net_xml = TEMPLATE_NETZ.replace('$clientnetz', 'Clientnetz-'+domain)
    try:
        net = libvirt_connection.networkDefineXML(net_xml)
        net.setAutostart(1)
        net.create()
    except:
        print('Network exists already')

def __getSerialPath():
    global gluon_domain
    domain_xml = gluon_domain.XMLDesc()
    xml_root = ET.fromstring(domain_xml)
    devices = xml_root.find('devices')
    console = devices.find('console')
    serialPath = console.get('tty')
    return serialPath



download_image_file_and_unzip_it(sys.argv[1])
open_libvirt_connection()
extract_domain()
setup_clientnetz()
install_vm()

