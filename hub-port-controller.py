'''
hub-port-controller

Copyright (c) 2020 S.K. Technology Firm, @GuriTech

Released under the MIT License
'''


import usb
import argparse
import json
import sys
from pprint import pprint

PORT_POWER_FEATURE = 8

# Device Handler Function
def get_device(id_vendor, id_product, serial_number = None):
    for bus in usb.busses():
        for device in bus.devices:
            if device.idVendor == id_vendor and device.idProduct == id_product:
                if serial_number != None and serial_number == device.dev.serial_number:
                    return device
                
                elif serial_number == None:
                    return device

    raise ValueError('Device not found')

# USB Message Transfer Functions
def get_port_status(port_number, device_handle):
    bmRequestType       = 0b10100011
    bRequest            = 0x00
    wValue              = 0x00
    wIndex              = port_number
    data_or_wLength     = 4
    timeout             = 1000

    return device_handle.ctrl_transfer(bmRequestType,bRequest,wValue,wIndex,data_or_wLength,timeout)

def get_hub_desc(device_handle,usb_version):
    bmRequestType   = 0b10100000
    bRequest        = 0x06

    if usb_version == 2:
        wValue      = 41 << 8 # [0x29,0x00]
    elif usb_version == 3:
        wValue      = 42 << 8

    wIndex          = 0
    data_or_wLength = 1024
    timeout = 1000

    def parse_desc(raw_desc):
        parsed_desc = {}
        offset = 0

        for n in list(raw_desc):
            if offset == 0:
                parsed_desc["bDescLength"] = n
            elif offset == 1:
                parsed_desc["bDescriptorType"] = n
            elif offset == 2:
                parsed_desc["bNbrPorts"] = n
            elif offset == 3:
                parsed_desc["wHubCharacteristics"] = [n]
            elif offset == 4:
                parsed_desc["wHubCharacteristics"].append(n)
            elif offset == 5:
                parsed_desc["bPwrOn2PwrGood"] = n
            elif offset == 6:
                parsed_desc["bHubContrCurrent"] = n
            elif offset == 7:
                parsed_desc["DeviceRemovable"] = n
            else:
                if "PortPwrCtrlMask" not in parsed_desc.keys():
                    parsed_desc["PortPwrCtrlMask"] = [n]
                else:
                    parsed_desc["PortPwrCtrlMask"].append(n)

            offset += 1

        return parsed_desc

    return parse_desc(device_handle.ctrl_transfer(bmRequestType,bRequest,wValue,wIndex,data_or_wLength,timeout))

def clear_port_feature(device_handle, port_number, feature):
    bmRequestType   = 0b00100011
    bRequest        = 0x01
    wValue          = feature
    wIndex          = port_number
    data_or_wLength = 0
    timeout         = 1000

    return device_handle.ctrl_transfer(bmRequestType,bRequest,wValue,wIndex,data_or_wLength,timeout)

def set_port_feature(device_handle, port_number, feature):
    bmRequestType   = 0b00100011
    bRequest        = 0x03
    wValue          = feature
    wIndex          = port_number
    data_or_wLength = 0
    timeout         = 1000

    return device_handle.ctrl_transfer(bmRequestType,bRequest,wValue,wIndex,data_or_wLength,timeout)

# Sub Routines
def restart_usb_device(hub_id_vendor, hub_id_product, port_numbers, hub_serial_number = None, usb_version = 2):
    hub = get_device(hub_id_vendor, hub_id_product, hub_serial_number)

    hub_description = get_hub_desc(hub.dev, usb_version)
    bNbrPorts = hub_description["bNbrPorts"]

    # Check Port Number
    for port_number in port_numbers:
        if 1 > port_number or bNbrPorts < port_number:
            raise IndexError("Port index out of range")

    # Port Power Off
    for port_number in port_numbers:
        clear_port_feature(hub.dev, port_number, PORT_POWER_FEATURE)

    # Port Power On
    for port_number in port_numbers:
        set_port_feature(hub.dev, port_number, PORT_POWER_FEATURE)

def get_ports_status(hub_id_vendor, hub_id_product, hub_serial_number = None, usb_version = 2):
    port_statuses = {}

    hub = get_device(hub_id_vendor, hub_id_product, hub_serial_number)

    hub_description = get_hub_desc(hub.dev, usb_version)
    bNbrPorts = hub_description["bNbrPorts"]

    for port_number in range(bNbrPorts):
        port_statuses[str(port_number + 1)] = get_port_status(port_number + 1, hub.dev)

    return port_statuses

# Main Routine
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('hub_id_vendor')
    parser.add_argument('hub_id_product')
    parser.add_argument('-s', '--hub_serial_number')
    parser.add_argument('-v', '--usb_version', type = int, default = 2)
    parser.add_argument('-p', '--port_numbers')
    parser.add_argument('-d', '--display_port_status', action = "store_true")

    args = parser.parse_args()

    hub_id_vendor       = int(args.hub_id_vendor,16)
    hub_id_product      = int(args.hub_id_product,16)
    hub_serial_number   = args.hub_serial_number
    usb_version         = args.usb_version

    if args.port_numbers != None:
        port_numbers        = json.loads(args.port_numbers)
    else:
        port_numbers        = []

    try:
        if args.display_port_status:
            pprint(get_ports_status(hub_id_vendor, hub_id_product, hub_serial_number = hub_serial_number, usb_version = usb_version))
        else:
            restart_usb_device(hub_id_vendor, hub_id_product, port_numbers,hub_serial_number = hub_serial_number, usb_version = usb_version)

    except Exception as e:
        tb = sys.exc_info()[2]
        print("{0}".format(e.with_traceback(tb)))

if __name__ == '__main__':
    main()
