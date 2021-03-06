#!/bin/usr/python3 -B
# -*- coding: utf-8 -*-

'''This is all of the radio related magic that happens in the Beep Inn project.
We are running the python rtlsdr module and tweaking the early examples.
'''

# Futures
from __future__ import print_function

# Standard Imports
import math
import statistics as stats
import time

# Non-standard Imports
import matplotlib.pyplot as plt
import numpy as np

# Local Imports
from rtlsdr import RtlSdr
from . import Config, Detect_Peaks

class SDRTools():
	'''RTLSDR class handles all of the SDR related commands
	'''
	# Define the source we are using in everything here.
	sdr = RtlSdr()
	cfg = Config.Configurator()

	# Local variable(s)
	cnt = ''
	backupcount = 1
	fig = plt.figure()
	image = -100*np.ones((100, 1024))
	samples = []
	gui_switch = False
	csv_switch = False
	gpstimestart = ''

	# Plotting Variables
	# Values are pulled from config file.
	nfft = int(cfg.value('Plot_Values', 'nfft_count'))
	samp = int(cfg.value('Plot_Values', 'samplemod_count'))
	thresh = float(cfg.value('Plot_Values', 'peakthresh'))
	pkdist = int(cfg.value('Plot_Values', 'peakdistance'))

	def __init__(self):
		# Pull device initial values from config file
		self.sdr.sample_rate = float(self.cfg.value('SDR_Values', 'sampleratehz'))
		self.sdr.freq_correction = int(self.cfg.value('SDR_Values', 'correctionppm'))
		self.sdr.gain = int(self.cfg.value('SDR_Values', 'gain'))
		# Make sure our counter is at zero when we startup
		self.cnt = 0
		# Init an animate-able plot with axes
		self.fig.add_subplot(1, 1, 1)
		plt.xlabel('Frequency (MHz)')
		plt.ylabel('Relative power (dB)')
		# Write a new temporary output file
		self.gpscoord()
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
		if self.gui_switch:
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
		# Dirty pattern suppression
		intense[512] = (float(intense[511]) + float(intense[513]))/2
		# We find local peaks from the intensity 1D
		peaks = Detect_Peaks.detect_peaks(intense, threshold=self.thresh*max(intense),\
			mpd=self.pkdist, show=False)

		#with open("test.csv", "w") as fff:
			#for i in range(0, len(intense)):
				#theline = str(intense[i]) + '\n'
				#fff.write(theline)

		lowvals = []
		for i in intense:
			if i not in peaks:
				lowvals.append(i)

		for i in peaks:
			if self.gui_switch:
				print((str(i) + ',' + str(intense[i])))
				plt.Circle((i,intense[i]), radius= 2)
			peakhgt = 10*math.log10(intense[i])
			low = 10*math.log10(stats.median(lowvals))
			print(lowvals)
			self.record_values(low, figure[i], peakhgt)
		# Put the figure in the image storage hole.  This can really be done in one step, but
		# this is done in case we want to doctor "figure" during the cycle"
		self.image = figure
		self.backup_csv()
		return

	def record_values(self, low, peakfreq, peakhgt):
		'''Records the values as we go along.
		Puts things into a temporary csv file.
		If there is a 'hit', the hit logged in a column.
		Otherwise, this is left blank.
		'''
		with open(str(self.cfg.localpath() + '/temp.csv'), 'a') as fff:
			fff.write(str(time.time()) + ',' + str(self.sdr.center_freq) + ',' + str(peakfreq) +\
				',' + str(low) + ',' + str(peakhgt) + '\n')
		return

	def gpscoord(self):
		'''Checks if GPS is enabled in the system.
		If it is, gets coordinates from gpsd.
		Sends as string.
		'''
		import calendar
		import datetime
		import serial

		gptime = ''
		gplong = ''
		gplati = ''
		while not (gptime and gplong and gplati):
			with serial.Serial('/dev/ttyAMA0', 9600, timeout=1) as ser:
				line = ser.readline()
				line = str(line.decode('utf-8'))
				print(line)
				result = [x.strip() for x in line.split(',')]

				if "GPRMC" in result[0]:
				#$GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*6A
				#Where:
				#RMC          Recommended Minimum sentence C
				#123519       Fix taken at 12:35:19 UTC
				#A            Status A=active or V=Void.
				#4807.038,N   Latitude 48 deg 07.038' N
				#01131.000,E  Longitude 11 deg 31.000' E
				#022.4        Speed over the ground in knots
				#084.4        Track angle in degrees True
				#230394       Date - 23rd of March 1994
				#003.1,W      Magnetic Variation
				#*6A          The checksum data, always begins with *
					convunix = result[1][0:2] + ',' + result[1][2:4] + ',' + result[1][4:] + ',' +\
						result[9][0:2] + ',' + result[9][2:4] + ',' + result[9][4:]
					gptime = calendar.timegm(datetime.datetime.strptime(convunix,\
						"%H,%M,%S.%f,%d,%m,%Y").timetuple())

				elif "GPGGA" in result[0]:
				# $GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47
				#Where:
				#GGA          Global Positioning System Fix Data
				#123519       Fix taken at 12:35:19 UTC
				#4807.038,N   Latitude 48 deg 07.038' N
				#01131.000,E  Longitude 11 deg 31.000' E
				#1            Fix quality: 0 = invalid
					#1 = GPS fix (SPS)
					#2 = DGPS fix
					#3 = PPS fix
					#4 = Real Time Kinematic
					#5 = Float RTK
					#6 = estimated (dead reckoning) (2.3 feature)
					#7 = Manual input mode
					#8 = Simulation mode
				#08           Number of satellites being tracked
				#0.9          Horizontal dilution of position
				#545.4,M      Altitude, Meters, above mean sea level
				#46.9,M       Height of geoid (mean sea level) above WGS84
					#ellipsoid
				#(empty field) time in seconds since last DGPS update
				#(empty field) DGPS station ID number
				#*47          the checksum data, always begins with *
					gplati = result[2] + result[3]
					gplong = result[4] + result[5]
				else:
					pass
			if gptime:
				print(gptime)
			else:
				print("WAITING...")
			if gplong:
				print(gplong)
			else:
				print("WAITING...")
			if gplati:
				print(gplati)
			else:
				print("WAITING...")
		with open(str(self.cfg.localpath() + '/temp.csv'), 'w') as fff:
			fff.write("Latitude, Longitude, Corrected Start Time\n")
			relinf = str(gplati) + ',' + str(gplong) + ',' + str(gptime) + '\n'
			fff.write(relinf)
			fff.write('Time(s UTC unix), Scan Freq(Hz), Peak Freq(Hz), Amp_baseline(dB), Amp_Hit(dB)\n')
		self.gpstimestart = gptime
		return

	def backup_csv(self):
		'''This function determines the amount of time which has passed since the start.
		If it has passed a certain threshold, it calls a function to save the temp.csv to the thumbdrive.
		'''
		# Check if time difference is 10 minutes.
		if (int(time.time()) - int(self.gpstimestart))/self.backupcount > 600:
			ret = self.perform_save
			if ret == 1:
				self.backupcount += 1
			else:
				print("Something went wrong backing up the file")
		return

	def perform_save(self):
		''' This function backs up the file from temporary to permanent storage.
		This is called by backup_csv, and called once directly during shutdown
		'''
		from shutil import copyfile
		print(self.cfg.localpath(), type(self.cfg.localpath()))
		print(self.gpstimestart, type(self.gpstimestart))
		if self.gpstimestart:
			copyfile(str(self.cfg.localpath() + '/temp.csv'), \
				str('/media/pi/BEEPDRIV/' + str(self.gpstimestart) + '.csv'))
			return 1
		return 0
