#!/bin/usr/python3 -B
# -*- coding: utf-8 -*-

'''This file holds argument information for the Beep_Inn program
'''

class Args():
	'''This is the argument class container
	'''

	#from types import SimpleNamespace
	# Locals
	#arg = SimpleNamespace()

	def __init__(self):
		'''Get the arguments
		'''
		self.arg = self.get_parser().parse_args()
		if self.arg.gui:
			self.guiinit()

	def get_parser(self):
		'''Get parser object for script processor.py
		'''
		from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
		parser = ArgumentParser(description=__doc__, formatter_class=ArgumentDefaultsHelpFormatter)
		parser.add_argument("-f", "--file", dest="filename", required=True,\
			type=lambda x: self.is_valid_file(parser, x),\
				help="input file with a line-broken frequency values (see example)", metavar="FILE")
		#parser.add_argument("-m", "--mode", dest="mode", required=True, type=int,\
			#help="Test")
		parser.add_argument("-g", "--gui", dest="gui", action="store_true", default=False,\
			help="Enables the graphical interface")
		parser.add_argument("-t", "--threshold", dest="thresh", type=float, default=30,\
			help="sets beep threshold amplitude in dB.")
		#parser.add_argument("-q", "--quiet",
							#action="store_false",
							#dest="verbose",
							#default=True,
							#help="don't print status messages to stdout")
		return parser

	def is_valid_file(self, parser, arg):
		'''
		Check if arg is a valid file that already exists on the file system.
		Else, die
		'''

		import os
		import sys

		arg = os.path.abspath(arg)
		if not os.path.exists(arg):
			parser.error("Input file specified %s does not exist" % arg)
			sys.exit(1)
		else:
			return arg

	def guiinit(self):
		'''Tells Beep_Inn to start the GUI
		'''
		from . import GuiFramework
		return
