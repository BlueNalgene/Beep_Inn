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
import os
#import sys
import time
import traceback

# Non-standard Imports


# Local Imports
#from rtlsdr import RtlSdr
from Beep_Inn_Classes import Arg, Config

#RADIO = RTLSDR.RTLSDR()

def main(hzfile):
	'''Main print_function
	'''

	#while True:
		## Lazy try/except to start count
		#try:
			#cnt = RADIO.hz_cycle(hzlist, cnt)
		#except UnboundLocalError:
			#cnt = RADIO.hz_cycle(hzlist)
		###RADIO.get_points()
		#RADIO.startup()
		#RADIO.refresher()
		#time.sleep(0.5)

if __name__ == '__main__':
	arg = Arg.Args()
	arg = arg.get_parser().parse_args()
	Config.Configurator()
	try:
		main(arg.filename)
	except KeyboardInterrupt:
		print("closing")
	except Exception as inst:
		traceback.print_exc()
		raise # reraises the exception
	finally:
		RADIO.close_sdr()
		quit()
