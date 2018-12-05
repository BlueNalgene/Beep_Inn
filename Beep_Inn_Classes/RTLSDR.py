#!/bin/usr/python3 -B
# -*- coding: utf-8 -*-

'''This is all of the radio related magic that happens in the Beep Inn project.
We are running the python rtlsdr module and tweaking the early examples.
'''

# Futures
from __future__ import print_function

# Standard Imports
import math
import sys
#import time

# Non-standard Imports
#from pylab import psd, xlabel, ylabel, show, waitforbuttonpress
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as sig

# Local Imports
from rtlsdr import RtlSdr
from Config import Configurator

class RTLSDR():
	'''RTLSDR class handles all of the SDR related commands
	'''
	# Define the source we are using in everything here.
	sdr = RtlSdr()
	cfg = Configurator()

	# Local variable(s)
	cnt = ''
	fig = plt.figure()
	image = -100*np.ones((100, 1024))
	samples = []

	# Plotting Variables
	nfft = int(cfg.value('Plot_Values', 'nfft_count'))
	samp = int(cfg.value('Plot_Values', 'samplemod_count'))

	def __init__(self):
		# Pull device initial values from config file
		self.sdr.sample_rate = float(self.cfg.value('SDR_Values', 'sampleratehz'))
		self.sdr.freq_correction = int(self.cfg.value('SDR_Values', 'correctionppm'))
		self.sdr.gain = self.cfg.value('SDR_Values', 'gain')
		# Make sure our counter is at zero when we startup
		self.cnt = 0
		self.init_plot()
		return

	def rtl_settings(self, hzfile):
		'''Reads the current setting from a counter.
		Then implements that setting.
		Then increments the counter.
		'''
		hzlist = []
		print("Frequencies found in list file " + str(hzfile))
		with open(hzfile, "r") as fff:
			for line in fff:
				try:
					hzlist.append(float(line))
					print(line[:-1] + " Hz")
				except ValueError:
					pass
		return hzlist

	def hz_cycle(self, hzlist, cnt=-1):
		'''Cycles through the list of known frequencies to monitor
		Sets on each one, performs test, and moves on.
		Default cycle starts at 0 (skips the first -1 value)
		'''
		cnt += 1
		if cnt == len(hzlist):
			cnt = 0
		self.sdr.center_freq = hzlist[cnt]
		return cnt

	def get_points(self):
		'''Gets the samples and stores them in the local.
		'''
		number = self.samp*self.nfft
		self.samples = self.sdr.read_samples(number)
		return

	def close_sdr(self):
		'''Does what it says on the tin.
		'''
		self.sdr.close()
		return

	def init_plot(self):
		'''This just starts the drawing function for the first time and allows it to refresh.
		TODO roll into __init__
		'''
		self.fig.add_subplot(1,1,1)
		self.samples = self.get_points()
		plt.xlabel('Frequency (MHz)')
		plt.ylabel('Relative power (dB)')
		return

	def refresher(self):
		'''Draws a new plot on the screen with each pass.  Useful for debugging.
		'''
		# We need to redeclare these for each cycle since this will be changing.
		ffcc = self.sdr.center_freq/1e6
		ffss = self.sdr.sample_rate/1e6
		self.get_points()
		# Returns the figure as well as a 1D plot of the intensities.
		aaa, figure = plt.psd(self.samples, self.nfft, ffss, ffcc)
		plt.xlabel('Frequency (MHz)')
		plt.ylabel('Relative power (dB)')
		# We find local peaks from the intensity 1D
		peaks, _ = sig.find_peaks(aaa, prominence=1)
		print("frame")
		for i in peaks:
			# TODO Does this work?
			peakloc = int(ffcc*ffss)*i-int(ffcc)
			peakhgt = 10*math.log10(aaa[i])
			print(peakloc, peakhgt)
		# Put the figure in the image storage hole.  This can really be done in one step, but
		# this is done in case we want to doctor "figure" during the cycle"
		self.image = figure
		#return self.image
		return

	def startup(self):
		'''
		TODO currently is running every cycle.  May be able to just run once or go in refresher.
		'''
		blit = False
		self.fig.canvas.draw()
		plt.pause(0.05)
		plt.clf
		self.fig.canvas.flush_events()
		return
