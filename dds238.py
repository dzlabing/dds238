#!/usr/bin/python3

# 2024-04-19 Read Hiking DDS238-2 ZN/S energy meter using Modbus via RS485 via USB

# install packages pyserial (not serial!) and pymodbus[serial]

# Registers
# https://github.com/fawno/Modbus/blob/4871fe24a342eee4f0db33d28968e37483ad3f1d/DDS238-2%20ZN-S%20Modbus.md

# Smart meter connected to USB
# PIN 1 = RS485 B
# PIN 2 = RS485 A

# USB dongle e.g. Amazon B09SB85W3J - ID 1a86:7523 QinHeng Electronics CH340 serial converter

# https://pymodbus.readthedocs.io/en/latest/source/client.html
from pymodbus.client import ModbusSerialClient
from serial import *

import logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.ERROR)

def run():
    client = ModbusSerialClient(method='rtu', port='/dev/ttyUSB0', baudrate=9600, parity='N', bytesize=8, stopbits=1, timeout=1)
    client.connect()
    request = client.read_holding_registers(0x0,0x1b,unit=10,slave=1)
    # Example register values
    # [0, 7133, 513, 0, 0, 0, 0, 0, 0, 2399, 0, 4733, 2327, 0, 0, 0, 1000, 4998, 0, 0, 0, 257, 0, 0, 0, 0]
    print("Registers: ",request.registers)
    print("Total energy", (request.registers[0x0]*0xffff+request.registers[0x1])/100," kWh");
    print("Exported energy ", (request.registers[0x8]*0xffff+request.registers[0x9])/100, " kWh");
    print("Imported energy ", (request.registers[0xa]*0xffff+request.registers[0xb])/100, " kWh");
    print("Voltage ", request.registers[0xc]/10, " V");
    print("Current ", request.registers[0xd]/100 ," A");
    print("Active power ", request.registers[0xe]/10, " W");
    print("Reactive power ", request.registers[0xf]/10, " VAr");
    print("Power factor ", request.registers[0x10]/1000, "");
    print("Frequency" , request.registers[0x11]/100," Hz");
    print("Modbus address ", request.registers[0x15]>>0x8, "");
    print("BitrateEnum ", request.registers[0x15]&0xf,"");
    print("Relais ", request.registers[0x1a],"");
    # The meter does not understand the 'write sigle register' function code (06h), only the 'write multiple registers' function code (10h).
    # Reset fails
    # request = client.write_registers(address=0x0,values=[0x0,0x0],unit=10,slave=1)
    
    client.close()

run()