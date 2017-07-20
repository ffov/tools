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
    <controller type='virtio-serial' index='0'>
      <alias name='virtio-serial0'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x07' function='0x0'/>
    </controller>
    <interface type='network'>
      <mac address='52:54:00:12:db:a1'/>
      <source network='Clientnetz-Dom16'/>
      <target dev='vnet17'/>
      <model type='virtio'/>
      <alias name='net0'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>
    </interface>
    <interface type='network'>
      <mac address='52:54:00:be:09:ba'/>
      <source network='default'/>
      <target dev='vnet18'/>
      <model type='virtio'/>
      <alias name='net1'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x04' function='0x0'/>
    </interface>
    <serial type='pty'>
      <source path='/dev/pts/14'/>
      <target port='0'/>
      <alias name='serial0'/>
    </serial>
    <console type='pty' tty='/dev/pts/14'>
      <source path='/dev/pts/14'/>
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
    <memballoon model='virtio'>
      <alias name='balloon0'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x09' function='0x0'/>
    </memballoon>
  </devices>
</domain>"""

def download_image_file(link):
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

def install_vm():
    global TEMPLATE
    global name
    global libvirt_connection
    xml = TEMPLATE.replace('$vmName', 'Test').replace('$imagePath', DEFAULT_DESTINATION_PATH).replace('$vmIMG', name.replace(".gz",""))
    libvirt_connection = libvirt.open(LIBVIRT_SYSTEM_PATH) 
    libvirt_connection.createXML(xml)

   




download_image_file(sys.argv[1])
install_vm()
   
