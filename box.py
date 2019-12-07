import sys, inspect
from abc import ABCMeta, abstractmethod
from exceptions import *

class BoxABC(metaclass=ABCMeta):
	''' Protocol for Box-like classes '''
	@abstractmethod
	def lock(self): pass
	@abstractmethod
	def open(self): pass
	@abstractmethod
	def put(self): pass
	@abstractmethod
	def fetch(self): pass
	@abstractmethod
	def destroy(self): pass
	@abstractmethod
	def empty(self): pass

	def internal(cls):
		# method hoisted up here so usable by BoxABC subclasses
		# checks if request from an expected class method
		frame = sys._getframe()
		caller = frame.f_back.f_code.co_name
		# caller is name of calling function but
		# it is possible to hack this by defining an outside function
		# and then calling <obj>.<method> from there. BUT for these cases
		# the frame globals dict will have the function name as a key but
		# this is not the case if caller is an inside method ...
		if caller not in frame.f_globals and \
			caller in dir(cls):
			# and is a method of cls so avoids naked <obj>.<attr> calls
			# from the outside (i.e. not from inside an outside functions)
			# in these cases -> caller is '<module>' and won't be in dir(cls)
			return True
		return False

class BoxList(list):
	''' variant of Python's list to store Box contents '''
	
	# here's a list of methods we need
	implement = [
		'__new__', '__init__', '__str__', '__repr__', '__doc__', '__dir__',
		'__iter__', '__len__', '__contains__', '__getitem__', 
		'__getattribute__','__eq__',
		'index', 'count',  ]
	# disable methods we don't want accessible i.e. the rest
	for i in dir(list):
		if i not in implement:
			code = exec(f'def {i}(self): raise BoxImplementationError(' +
										'"{i} is not implemented")')

	@classmethod
	def internal(cls, caller):
		# check if request is from inside a Box-type subclass
		frame = sys._getframe()
		# caller is name of calling function but
		# it is possible to hack this by defining an outside function
		# and then calling <obj>.method from there. BUT for these cases
		# the frame globals dict will have the function name as a key but
		# this is not the case if caller is an inside method ...
		if caller not in frame.f_globals and \
			caller in dir(Box):
			# and is a method of cls so avoids naked <obj>.method calls
			# from the outside (i.e. not from inside an outside functions)
			# in these cases -> caller is '<module>' and won't be in dir(Box)
			return True
		return False

	def append(self, item):
		# we get calling func here instead of inside 'internal' classmethod
		# here: caller = Box.method e.g. 'put' <- what we want
		# inside 'internal': this.append <- not what we want
		caller = sys._getframe().f_back.f_code.co_name
		if BoxList.internal(caller):
			super().append(item)

	def remove(self, item):
		caller = sys._getframe().f_back.f_code.co_name
		if BoxList.internal(caller):
			super().remove(item)

	def clear(self):
		caller = sys._getframe().f_back.f_code.co_name
		if BoxList.internal(caller):
			super().clear()
		
class Box(BoxABC):
	'''
		Creates boxes for keeping data 'relatively' safe

		Often we pass data/collections around a program that we
		don't want changed without our knowledge in another part of the program.
		The intention behind this class is to avoid inadvertent data tampering
		It's NOT intended to prevent hacking the data by those who know how.

		Boxes can be locked to stop their contents being amended.
		Although a BoxList (stores the box's contents) inherits from the 
		bog-standard Python list object many attributes have been disabled. 
		For instance you cannot natively assign to a box. Instead you use 
		special methods for storage ('put') and retrieval. 

		Use:
		# see the docs
	'''

	_accepts = [
		str, 
		list,
		tuple,
		dict,
		set,
		frozenset, 
		int,
		float,
		complex,
	]

	_mutables = [list, tuple, dict, set]
	_names_dict = {}
	
	def __init__(self, *, key, name=None, itype=None):
		self.keyset = False
		self.key = key
		self.name = name
		self.itype = itype
		self.contents = BoxList()
		self.isopen = True

	@property
	def key(self):
		# only release key if request from class method
		if super().internal():
			return self.__key
		raise BoxKeyAccessError('You cannot directly access a key')

	@key.setter
	def key(self, key):
		if not self.keyset: 
			# can set first time only; store in double _ to enforce mangling 
			# and frustrate attempt to access from outside the class
			self.__key = key
			self.keyset = True
		else: # can't reset keys after init
			raise BoxKeyAccessError('Keys cannot be reset')

	@property
	def contents(self):
		''' define contents as property to set as read only '''
		return self.__contents

	@contents.setter
	def contents(self, item):
		''' only accept an empty BoxList 

			prevents assignment statements <box>.contents = [something] or
			<box>.contents = [alist] + <box>.contents
			nb. ... = <box>.contents + [alist] fails b/c __add__ not implemented
		'''
		if len(item) == 0:
			self.__contents = item

	def _key_check(self, key):
		if not self.isopen:
			if key is None:
				raise BoxLockedError('Box is locked. Provide a key')
			elif key != self.key:
				raise BoxKeyAccessError('Wrong key')
		return True

	def _type_check(self, item):
		if self.itype is not None:
			if not isinstance(item, self.itype):
				raise BoxItemTypeError(f'item {item} must be of box type {self.itype}')
		elif type(item) not in self._accepts:
			raise BoxItemTypeError(f'item {item} must be one of {self._accepts}')
		return True

	def _kw_check(self, kw, exp, typ):
		if not isinstance(kw, typ):
			raise BoxExceptionError(f'Expected {exp} of type {typ.__name__}')
		return True

	def _index_check(self, index):
		if index < 0 or index > len(self.contents) - 1:
			raise BoxItemAccessError('Index out of range')
		return True

	def _with_names(self):
		return [(name, type(item).__name__) for 
						name, item in self._names_dict.items()]

	def _without_names(self):
		return [(None, type(item).__name__) for item in self.contents if 
					item not in self._names_dict.values()]

	def _name_check(self, name):
		return name in self._names_dict

	def _named_check(self, item):
		return item in self._names_dict.values()

	def _name_pass(self, name1=None, name2=None, action=None):
		''' checks for setting, deleting, renaming names '''
		
		if action == 'setname':
			if self._name_check(name1):	# name used already
				raise BoxNameError('This name already exists. Try another')
		
		elif action == 'rename':
			if name1 is None or name2 is None:
				raise BoxNameError('Provide both old, new names as arguments')
			if not self._name_check(name1):
				raise BoxNameError('The old name does not exist')
			if self._name_check(name2):
				raise BoxNameError('This name already exists. Pick another')

		elif action == 'delname':
			if not self._name_check(name1):
				raise BoxNameError('This name does not exist')
		
		return True

	def put(self, item, name=None, key=None):
		if self._key_check(key) and self._type_check(item):
			# copy mutables so can't be changed from outside box
			if type(item) in self._mutables:
				from copy import deepcopy
				item = deepcopy(item)

			# cache name and save
			if name is not None: 
				self._names_dict[name] = item
			self.contents.append(item)

	def contains(self, item):
		if not self.isopen:
			raise BoxLockedError('Box is locked. Provide a key')
		return item in self.contents

	def __get__(self, **kwargs):
		''' takes item out of box '''

		action = kwargs.get('action')
		name = kwargs.get('name')
		index = kwargs.get('index')
		item = kwargs.get('item')
		
		if not self.isopen:
			raise BoxLockedError('Box is locked. Provide a key')

		if name is not None:
			if self._kw_check(name, 'name', str):
				item = self._names_dict.get(name)
		
		elif index is not None:
			if self._kw_check(index, 'index', int):
				if self._index_check(index):
					item = self.contents[index]
		
		elif item is not None:
			if not self.contains(item):
				item = None

		if item is None:
			raise BoxItemAccessError(f'Box does not have requested item')
		else:
			if action in ['fetch', 'destroy']: 
				self.contents.remove(item)	
			if action in ['fetch', 'use']: 
				return item

	def fetch(self, /, **kwargs):
		return self.__get__(action='fetch', **kwargs)

	def use(self, /, **kwargs):
		return self.__get__(action='use', **kwargs)

	def destroy(self, /, **kwargs):
		self.__get__(action='destroy', **kwargs)

	def lock(self, key):
		if self._key_check(key):
			self.isopen = False

	def open(self, key):
		if self._key_check(key):
			self.isopen = True

	def getnames(self, key=None):
		if self._key_check(key):
			return self._with_names() + self._without_names()

	def setname(self, index, name, key=None):
		''' only for items without names '''
		if self._key_check(key) and \
			self._index_check(index):
			if self._name_pass(name, action='setname'):	# name not used already
				it = self.contents[index]
				if self._named_check(it):	# item named previously
					raise BoxNameError('This item already has a name')
				self._names_dict[name] = it

	def rename(self, old=None, new=None, key=None):
		''' only for items with names '''
		if self._key_check(key):
			if self._name_pass(old, new, action='rename'):
				self._names_dict[new] = self._names_dict[old]
				del self._names_dict[old]

	def delname(self, name=None, key=None):
		''' only for items with names '''
		if self._key_check(key):
			if self._name_pass(name):
				del self._names_dict[name]

	def empty(self, key=None):
		if self._key_check(key):
			return self.contents.clear()
			
	@property
	def isempty(self):
		return self.contents == []

	def __str__(self):
		return self.name or 'A Box'

class Crate(Box):
	''' store boxes '''
	def __init__(self, *, key, name='Crate', itype=Box):
		super().__init__(key=key, name=name, itype=itype)
	def contains(self):
		''' because can't use names yet to select boxes '''
		return NotImplemented

class Container(Box):
	''' store crates '''
	def __init__(self, *, key, name='Container', itype=Crate):
		super().__init__(key=key, name=name, itype=itype)
	def contains(self):
		''' because can't use names yet to select crates '''
		return NotImplemented





