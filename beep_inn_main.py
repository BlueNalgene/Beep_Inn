#!/bin/usr/python3 -B
# -*- coding: utf-8 -*-

'''This is the frontend for an experimental version of the Beep Inn project.
This script scans radio frequencies using an RTL-SDR dongle.
Upon finding something, it records information about the find.
Uses Python3
'''

# Futures
from __future__ import print_function

# Standard Imports
import sys
import time
import traceback

# Non-standard Imports


# Local Imports
#from rtlsdr import RtlSdr
from Beep_Inn_Classes import RTLSDR

RADIO = RTLSDR.RTLSDR()

def main():
	'''Main print_function
	'''

	
	while True:
		RADIO.rtl_settings()
		#samples = RADIO.get_points()
		#RADIO.math_it(samples)
		RADIO.simple_samples(256)
		time.sleep(0.5)

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print("closing")
	except Exception as e:
		traceback.print_exc()
		raise # reraises the exception
	finally:
		RADIO.close_sdr()
		quit()
