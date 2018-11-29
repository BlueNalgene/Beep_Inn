#!/bin/usr/python3 -B
# -*- coding: utf-8 -*-

'''This is all of the radio related magic that happens in the Beep Inn project.
We are running the python rtlsdr module and tweaking the early examples.
'''

# Futures
from __future__ import print_function

# Standard Imports
#import time

# Non-standard Imports
#from pylab import psd, xlabel, ylabel, show, waitforbuttonpress
import matplotlib.pyplot as plt

# Local Imports
from rtlsdr import RtlSdr

class RTLSDR():
	'''RTLSDR class handles all of the SDR related commands
	'''
	# Define the source we are using in everything here.
	sdr = RtlSdr()

	# Local variable(s)
	cnt = ''

	def __init__(self):
		# Configure device with initial values.
		self.sdr.sample_rate = 2.048e6   # Hz
		self.sdr.center_freq = 70.0      # Hz
		self.sdr.freq_correction = 60    # PPM
		self.sdr.gain = 'auto'           # dB
		# Make sure our counter is at zero when we startup
		self.cnt = 0
		return

	def rtl_settings(self):
		'''Reads the current setting from a counter.
		Then implements that setting.
		Then increments the counter.
		'''
		if self.cnt > 4:
			self.cnt = 0
		if self.cnt == 0:
			self.sdr.center_freq = 150.0e6
		elif self.cnt == 1:
			self.sdr.center_freq = 150.5e6
		elif self.cnt == 2:
			self.sdr.center_freq = 151.0e6
		elif self.cnt == 3:
			self.sdr.center_freq = 151.5e6
		elif self.cnt == 4:
			self.cnt = 152.0e6
		else:
			# This should be unecessary.
			self.cnt = 0
		# Increment
		self.cnt += 1
		return

	def simple_samples(self, number):
		'''Gets a number of samples from receiver.
		'''
		print(self.sdr.read_samples(number))
		return

	def get_points(self, number):
		'''Just gets the samples are returns them.
		This is a more dynamic alternative to simple_samples
		'''
		samples = self.sdr.read_samples(number)
		return samples

	def math_it(self, samples):
		'''This function shows a frequency centered spectral plot of the data from samples
		'''
		plt.psd(samples, NFFT=1024, Fs=self.sdr.sample_rate/1e6, Fc=self.sdr.center_freq/1e6)
		plt.xlabel('Frequency (MHz)')
		plt.ylabel('Relative power (dB)')
		# Show the graph without blocking other calculations
		plt.show(block=False)
		# Pause for 1 second
		plt.pause(1)
		# Close graph
		plt.close()

	def close_sdr(self):
		'''Does what it says on the tin.
		'''
		self.sdr.close()
		return
