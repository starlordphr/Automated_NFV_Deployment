'''
This script handles parsing SLA configurations and
feeding them to console (ui)
'''

# Tutorial at:
# https://docs.python.org/2/library/configparser.html

import sys
from ConfigParser import ConfigParser

def parse_config(file):
	# global all constants

	cfg = ConfigParser()
	cfg.read(file)
