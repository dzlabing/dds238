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
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
# from pymodbus.payload import BinaryPayloadBuilder
from serial import *

import logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.ERROR)

def run():
    client = ModbusSerialClient(method='rtu', port='/dev/ttyUSB0', baudrate=9600, parity='N', bytesize=8, stopbits=1, timeout=1)
    client.connect()
    request = client.read_holding_registers(0x0,0x1b,unit=10,slave=1) # was 1b
    # Example register values
    # [0, 7133, 513, 0, 0, 0, 0, 0, 0, 2399, 0, 4733, 2327, 0, 0, 0, 1000, 4998, 0, 0, 0, 257, 0, 0, 0, 0]
    print("Registers: ",request.registers)

    # Total energy 71.33  kWh
    # Exported energy  47.34  kWh
    # Imported energy  23.99  kWh
    # Voltage  230.4  V
    # Current  0.62  A
    # Active power  131  W
    # Reactive power  -2  VAr
    # Power factor  0.917
    # Frequency 50.0  Hz
    # Modbus address  1
    # Bitrate  9600 bit/s
    # Relais  off


    # total energy - byte order big endian, unsinged dword 32bits
    a = request.registers[0x0:0x2]
    d = BinaryPayloadDecoder.fromRegisters(a,byteorder=Endian.BIG, wordorder=Endian.BIG)
    print("Total energy", d.decode_32bit_uint()/100," kWh");
    # exported energy, unsinged dword 32 bits
    a = request.registers[0x8:0xa]
    d = BinaryPayloadDecoder.fromRegisters(a,byteorder=Endian.BIG, wordorder=Endian.BIG)
    print("Exported energy ", d.decode_32bit_uint()/100, " kWh");
    # imported energy, unsinged dword 32 bits
    a = request.registers[0xa:0xb]
    d = BinaryPayloadDecoder.fromRegisters(a,byteorder=Endian.BIG, wordorder=Endian.BIG)
    print("Imported energy ",d.decode_32bit_uint()/100, " kWh");
    # voltage, unsigned word 16 bits
    a = request.registers[0xc:0xd]
    d = BinaryPayloadDecoder.fromRegisters(a,byteorder=Endian.BIG, wordorder=Endian.BIG)
    print("Voltage ", d.decode_16bit_uint()/10, " V");
    # current, unsigned word 16 bits
    a = request.registers[0xd:0xe]
    d = BinaryPayloadDecoder.fromRegisters(a,byteorder=Endian.BIG, wordorder=Endian.BIG)
    print("Current ", d.decode_16bit_uint()/100 ," A");
    # active power, signed word 16 bits
    a = request.registers[0x0e:0xf]
    d = BinaryPayloadDecoder.fromRegisters(a,byteorder=Endian.BIG, wordorder=Endian.BIG)
    print("Active power ", d.decode_16bit_int(), " W");
    # reactive power, signed word 16 bits
    a = request.registers[0xf:0x10]
    d = BinaryPayloadDecoder.fromRegisters(a,byteorder=Endian.BIG, wordorder=Endian.BIG)    
    print("Reactive power ",d.decode_16bit_int(), " VAr");
    # power factor, signed word 16 bits
    a = request.registers[0x10:0x11]
    d = BinaryPayloadDecoder.fromRegisters(a,byteorder=Endian.BIG, wordorder=Endian.BIG)    
    print("Power factor ", d.decode_16bit_int()/1000, "");
    # frequency, unsinged word 16 bits
    a = request.registers[0x11:0x12]
    d = BinaryPayloadDecoder.fromRegisters(a,byteorder=Endian.BIG, wordorder=Endian.BIG)    
    print("Frequency" , d.decode_16bit_int()/100," Hz");
    # address, signed byte, 8 bits    
    print("Modbus address ", request.registers[0x15]>>0x8, "");
    # bit rate enum 
    bitrate_enum = {
        1: 9600,
        2: 4800,
        3: 2400,
        4: 1200
    }  
    a = request.registers[0x15:0x16]
    if a[0]&0xf in bitrate_enum:
        print("Bitrate ", bitrate_enum[a[0]&0xf],"bit/s");
    # relais (0=off, 1=on) - only some models
    relais_enum = {
        0: "off",
        1: "on"
    }  
    a = request.registers[0x1a:0x1b]
    if a[0] in relais_enum:    
        print("Relais ", relais_enum[a[0]],"");
    # The meter does not understand the 'write sigle register' function code (06h), only the 'write multiple registers' function code (10h).
    # Reset fails
    # request = client.write_registers(address=0x0,values=[0x0,0x0],unit=10,slave=1)
    
    client.close()

run()