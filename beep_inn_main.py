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
from shutil import copyfile
#import sys
import time
import traceback

# Non-standard Imports

# Local Imports
from Beep_Inn_Classes import Arg, Config, Clockset, RTLSDR

RADIO = RTLSDR.SDR_Tools()
STARTTIME = int(time.time())

def main(hzfile, guiswitch):
	'''Main print_function
	'''
	# Set up the frequencies in a list
	hzlist = RADIO.rtl_settings(hzfile)
	# Send GUI info
	RADIO.is_gui(guiswitch)
	

	while True:
		# Lazy try/except to start count
		try:
			cnt = RADIO.hz_cycle(hzlist, cnt)
		except UnboundLocalError:
			cnt = RADIO.hz_cycle(hzlist)
		RADIO.refresher()
		time.sleep(0.01)

if __name__ == '__main__':
	arg = Arg.Args()
	arg = arg.get_parser().parse_args()
	Config.Configurator()
	#if arg.rtcgetter:
		#Clockset.rtc()
	if not os.path.isdir("/media/BEEPDRIV"):
		print("ERROR: no usb drive found at /media/BEEPDRIV")
		quit()
	try:
		main(arg.filename, arg.gui)
	except KeyboardInterrupt:
		print("closing")
	except Exception as inst:
		traceback.print_exc()
		raise # reraises the exception
	finally:
		RADIO.close_sdr()
		copyfile(str(os.path.dirname(os.path.abspath(__file__)) + '/temp.csv'), \
			str('/media/BEEPDRIV/' + STARTTIME + '.csv'))
		quit()
