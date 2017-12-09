from matplotlib import pyplot as plt
import numpy as np
import time

class PlotScheme:
	bgcolor='black'
	linecolor='green'

_xspan, _yspan = 0,0
_xsize = 256
_curr_line = None
is_open = False

_fig, _ax = 0,0
_footnote = None
_caption = None

# note: x_span is a number, while y_span is a tuple or list
def set_axis_span(x_span, y_span):
	global _xspan, _yspan
	_xspan = x_span
	_yspan = y_span

	_ax.set_xlim(_xspan)
	_ax.set_ylim(_yspan)
	#_ax.set_aspect(0.5 * _xspan / (_yspan[1] - _yspan[0]))

def get_axis_span():
	return _xspan, _yspan

def set_texts(xlabel=None, ylabel=None, caption=None):
	global _caption
	if xlabel != None:
		_ax.set_xlabel(xlabel)
	if ylabel != None:
		_ax.set_ylabel(ylabel)
	if caption != None:
		plt.title(caption)
		_caption = caption

def open_window(x_span=(0,1), y_span=(0,30), x_size=None):
	# initialization function
	global _fig, _ax, is_open, _footnote, _xsize
	if is_open:
		print "[visualizer.py] Window already opened!"
		return

	if type(x_size) == int:
		_xsize = x_size

	_fig, _ax = plt.subplots()
	_ax.set_axis_bgcolor(PlotScheme.bgcolor)
	# maybe set window size...
	set_axis_span(x_span, y_span)

	yrange = _yspan[1] - _yspan[0]
	_footnote = plt.text(0, _yspan[1] - yrange * 1.28, "")

	plt.ion()
	update_plot(np.zeros(_xsize))
	is_open = True

def close_window():
	global is_open
	if is_open:
		plt.close()
		is_open = False

def is_window_closed():
	if len(plt.get_fignums()) == 0:
		is_open = False
		return True
	else:
		return False

def update_plot(data, footnote=None, padding=True):
	global _curr_line, _footnote

	if _curr_line != None:
		for i in xrange(len(_curr_line)):
			_curr_line.pop(0).remove()

	x_span = np.linspace(_xspan[0], _xspan[1], len(data))
	if padding:
		data = list(data)	# in case data is numpy array
		x_span = np.linspace(_xspan[0], _xspan[1], _xsize)
		data += [0] * (_xsize - len(data))
	_curr_line = plt.plot(x_span, data, color=PlotScheme.linecolor)

	if footnote != None:
		_footnote.set_text(footnote)

	plt.pause(0.001)
