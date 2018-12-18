#!/usr/bin/python3
import serial
while True:
  with serial.Serial('/dev/ttyUSB0', 4800, timeout=1) as ser:
    line = ser.readline()
    print(line)
