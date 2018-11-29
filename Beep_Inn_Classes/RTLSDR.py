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
import time

# Non-standard Imports
#from pylab import psd, xlabel, ylabel, show, waitforbuttonpress
import matplotlib.pyplot as plt

# Local Imports
from rtlsdr import RtlSdr

class RTLSDR():
	'''RTLSDR class handles all of the SDR related commands
	'''
	sdr = RtlSdr()
	settingcounter = ''

	def __init__(self):
		# configure device
		self.sdr.sample_rate = 2.048e6   # Hz
		self.sdr.center_freq = 70.0 # Hz
		self.sdr.freq_correction = 60    # PPM
		self.sdr.gain = 'auto'
		self.settingcounter = 0
		return

	def rtl_settings(self):
		'''Reads the current setting from a counter.
		Then implements that setting.
		Then increments the counter.
		'''
		if self.settingcounter > 4:
			self.settingcounter = 0
		if self.settingcounter == 0:
			self.sdr.center_freq = 150.0e6 # Hz
		elif self.settingcounter == 1:
			self.sdr.center_freq = 150.5e6
		elif self.settingcounter == 2:
			self.sdr.center_freq = 151.0e6
		elif self.settingcounter == 3:
			self.sdr.center_freq = 151.5e6
		elif self.settingcounter == 4:
			self.settingcounter = 152.0e6
		else:
			self.settingcounter = 0
		self.settingcounter += 1
		return

	def get_points(self):
		'''Just gets the samples are returns them.
		'''
		samples = self.sdr.read_samples(256*1024)
		return samples

	def math_it(self, samples):

		plt.psd(samples, NFFT=1024, Fs=self.sdr.sample_rate/1e6, Fc=self.sdr.center_freq/1e6)
		plt.xlabel('Frequency (MHz)')
		plt.ylabel('Relative power (dB)')
		print("hat1")
		plt.show(block=False)
		plt.pause(1)
		plt.close()

	def close_sdr(self):
		'''Does what it says on the tin.
		'''
		self.sdr.close()
		return

	def simple_samples(self, number):
		'''Gets a number of samples from receiver.
		'''
		print(self.sdr.read_samples(number))
		return
