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
import time

# Non-standard Imports
#from pylab import psd, xlabel, ylabel, show, waitforbuttonpress
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
#import scipy.signal as sig
import peakutils

# Local Imports
from rtlsdr import RtlSdr
from . import Config

class SDR_Tools():
	'''RTLSDR class handles all of the SDR related commands
	'''
	# Define the source we are using in everything here.
	sdr = RtlSdr()
	cfg = Config.Configurator()

	# Local variable(s)
	cnt = ''
	fig = plt.figure()
	image = -100*np.ones((100, 1024))
	samples = []
	gui_switch = False
	csv_switch = False

	# Plotting Variables
	nfft = int(cfg.value('Plot_Values', 'nfft_count'))
	samp = int(cfg.value('Plot_Values', 'samplemod_count'))

	def __init__(self):
		# Pull device initial values from config file
		self.sdr.sample_rate = float(self.cfg.value('SDR_Values', 'sampleratehz'))
		self.sdr.freq_correction = int(self.cfg.value('SDR_Values', 'correctionppm'))
		self.sdr.gain = int(self.cfg.value('SDR_Values', 'gain'))
		# Make sure our counter is at zero when we startup
		self.cnt = 0
		# Init an animate-able plot with axes
		self.fig.add_subplot(1,1,1)
		plt.xlabel('Frequency (MHz)')
		plt.ylabel('Relative power (dB)')
		# Write a new temporary output file
		with open(str(self.cfg.localpath() + '/temp.csv'), 'w') as fff:
			fff.write('Time, Freq(Hz), Amp_baseline(dB), Amp_Hit(dB)\n')
		return

	def is_gui(self, guiarg):
		'''Activates a self switch to enable the gui interface,
		otherwise, it is set to false.
		'''
		self.gui_switch = guiarg
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

	def refresher(self):
		'''Draws a new plot on the screen with each pass.  Useful for debugging.
		'''
		# Set things for imported animated bits (aka, wait then clear)
		plt.pause(0.05)
		self.fig.clf()
		# We need to redeclare these for each cycle since this will be changing.
		ffcc = self.sdr.center_freq/1e6
		ffss = self.sdr.sample_rate/1e6
		self.get_points()
		# Returns the figure as well as a 1D plot of the intensities.
		intense, figure = plt.psd(self.samples, self.nfft, ffss, ffcc)
		plt.xlabel('Frequency (MHz)')
		plt.ylabel('Relative power (dB)')
		plt.ylim(-50, 10)
		# We find local peaks from the intensity 1D
		peaks = peakutils.indexes(intense, thres=0.02/max(intense), min_dist=100)

		lowvals = []
		for i in intense:
			if i not in peaks:
				lowvals.append(i)

		peakfreq = []
		for i in peaks:
			peakhgt = 10*math.log10(intense[i])
			peakfreq.append(figure[i])
			self.record_values(lowvals, peaks, figure[i])
		# Put the figure in the image storage hole.  This can really be done in one step, but
		# this is done in case we want to doctor "figure" during the cycle"
		self.image = figure
		return

	def record_values(self, lowvals, peaks, peakfreq):
		'''Records the values as we go along.
		Puts things into a temporary csv file.
		If there is a 'hit', the hit logged in a column.
		Otherwise, this is left blank.
		'''
		with open(str(self.cfg.localpath() + '/temp.csv'), 'a') as fff:
			fff.write(str(time.time()) + ',' + str(self.sdr.center_freq) + ',' +\
				str(sum(lowvals)/(self.nfft-len(peaks))) + ',' + str(peakfreq) + '\n')
		return
