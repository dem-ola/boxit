import sys, inspect, hashlib
from abc import ABCMeta, abstractmethod
from collections import namedtuple
from exceptions import *
from vessel import Vessel

class Box(Vessel):
	''' stores boxes '''
	def __init__(self, *, name=None, itype=None):
		super().__init__(name=name, itype=itype)
	def __str__(self):
		return 'Box' if self.name is None else self.name
	def __repr__(self):
		v = 'Box'
		return f'{v}()' if self.name is None else f"{v}(name='{self.name}')"

class Crate(Vessel):
	''' stores boxes '''
	def __init__(self, *, name=None, itype=Box):
		super().__init__(name=name, itype=itype)
	def __str__(self):
		return 'Crate' if self.name is None else self.name
	def __repr__(self):
		v = 'Crate'
		return f'{v}()' if self.name is None else f"{v}(name='{self.name}')"

class Container(Vessel):
	''' stores crates '''
	def __init__(self, *, name=None, itype=Crate):
		super().__init__(name=name, itype=itype)
	def __str__(self):
		return 'Container' if self.name is None else self.name
	def __repr__(self):
		v = 'Container'
		return f'{v}()' if self.name is None else f"{v}(name='{self.name}')"