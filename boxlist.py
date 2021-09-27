import sys, inspect, hashlib
from abc import ABCMeta, abstractmethod
from collections import namedtuple
from exceptions import *

class BoxList(list):
	''' variant of Python's list to store Box contents '''
	
	# methods we need; then we disable the rest - throw error if called
	implement = [
		'__new__', '__init__', '__str__', '__repr__', '__doc__', '__dir__',
		'__iter__', '__len__', '__contains__', '__getitem__', 
		'__getattribute__','__eq__',
		'index', 'count', 'insert' ]
	
	for i in dir(list):
		if i not in implement:
			code = exec(f'def {i}(self): raise BoxImplementationError(' +
										f'"{i} is not implemented")')

	@classmethod
	def internal(cls, caller):
		''' check if request is from inside a Box-type subclass '''
		# nb. diff to that in VesselABC
		frame = sys._getframe()
		if caller not in frame.f_globals and \
			caller in dir(Box):
			return True
		return False

	def append(self, item):
		# we get caller i.e. calling func here instead of inside 'internal'
		# here: caller = method that called append e.g. 'put' <- what we want
		# inside 'internal': would be append <- not what we want
		caller = sys._getframe().f_back.f_code.co_name
		if BoxList.internal(caller):
			super().append(item)

	def insert(self, position, item):
		caller = sys._getframe().f_back.f_code.co_name
		if BoxList.internal(caller):
			super().insert(position, item)

	def remove(self, item):
		caller = sys._getframe().f_back.f_code.co_name
		if BoxList.internal(caller):
			super().remove(item)

	def clear(self):
		caller = sys._getframe().f_back.f_code.co_name
		if BoxList.internal(caller):
			super().clear()