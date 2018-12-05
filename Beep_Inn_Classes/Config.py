#!/bin/usr/python3 -B
# -*- coding: utf-8 -*-

'''This class handles the reading and possibly writing of the config file.
'''

import os
import configparser

class Configurator():
	'''The Configurator handles the config file things for Beep Inn
	'''
	configpath = ''
	config = configparser.ConfigParser()

	def __init__(self):
		'''Initialize class
		declare path to ini file
		If it doesn't exist, create with defaults
		'''
		dirpath = str(os.path.dirname(os.path.abspath(__file__)))
		self.configpath = str(dirpath + '/config.ini')
		if not os.path.exists(self.configpath):
			print("WARNING: Config.ini does not exist, creating file with default values")
			self.default_gen()
		return

	def get_path(self):
		'''Returns the config path for reading
		'''
		return self.configpath

	def value(self, section, key):
		self.config.read(self.configpath)
		val = self.config.get(section, key)
		return val

	def default_gen(self):
		'''Just the defaults all packaged up
		'''
		self.config = configparser.ConfigParser()
		self.config['SDR_Values'] = {}
		self.config['Plot_Values'] = {}
		self.config['SDR_Values']['SampleRateHz'] = '1e6'
		self.config['SDR_Values']['CorrectionPPM'] = '60'
		self.config['Plot_Values']['NFFT_count'] = '1024'
		self.config['Plot_Values']['SampleMod_count'] = '256'
		self.config['SDR_Values']['Gain'] = 'auto'
		with open(self.configpath, 'w') as configfile:
			self.config.write(configfile)
		return
