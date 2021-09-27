import sys, inspect, hashlib
from abc import ABCMeta, abstractmethod
from collections import namedtuple
from exceptions import *


class VesselABC(metaclass=ABCMeta):
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

	@classmethod
	def internal(cls):
		''' checks if request is from an expected class method 
		
		We wish for some methods to be called only from class methods.
		A hack could:
		(A) call <instance>.<method> from an external function
		However, the frame globals dict will have the function name as a key 
		but this won't be the case if caller is an internal method.
		hence: ... caller not in frame.f_globals check ...
		(B) make a direct <instance>.<method> call (not from inside a function)
		but here caller is '<module>' and won't be in dir(cls)
		hence: ... caller in dir(cls) check ...
		
		'''
		frame = sys._getframe()
		caller = frame.f_back.f_code.co_name
		if caller not in frame.f_globals and \
			caller in dir(cls):
			return True
		return False

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

class Vessel(VesselABC):
	''' super class for various vessels '''

	_hash_dict = {}
	_mutables = [list, tuple, dict, set, frozenset]
	_accepts = _mutables + [str, int, float, complex]
	Item = namedtuple('Item', ['id', 'name', 'item', 'typ', 'vessel'])
	__items = BoxList()

	LOCKED_MSG = 'Box is locked. Provide a key to unlock.'
		
	def __init__(self, *, name=None, itype=None):
		self.isopen = True
		self.__keyset = False
		self.__itype = itype
		self.__items = BoxList()
		self.vessel = None
		# keep .name as last item!
		# b/c of _is_duplicates and b/c name prop returns
		# any attr below name won't be included in atrributes list
		self.name = name

	def get_caller(self, frame):
		return frame.f_back.f_code.co_name

	@property
	def key(self):
		# only release key if request from class method
		caller = self.get_caller(sys._getframe())
		if caller not in dir(Vessel):
			raise BoxKeyError('You cannot directly access a key')
		return self.__key

	@key.setter
	def key(self, key):
		caller = self.get_caller(sys._getframe())
		if caller == 'lock':
			if not self.__keyset: 
				# Store in double _ to enforce mangling 
				# and frustrate attempt to access from outside the class
				self.__key = key
				self.__keyset = True
			else:
				raise BoxKeyError('Keys cannot be reset.')
		else:
			raise BoxKeyError('Keys can only be set via lock method.')
			

	def __update__(self, action, item, name, oldhash=None):
		''' update hash_dict and __items list '''

		# vessels are usually doing that something to or with items so 
		# normally vessel = self; however we also want to add vessels on creation
		# to hash_dict but a vessel's vessel is not itself: here vessel = None
		vessel = self
		if self == item: vessel = None

		# delete entry with old name
		if action in ['del', 'reset']:
			olditem = Vessel._hash_dict[oldhash]
			vessel = olditem.vessel
			del Vessel._hash_dict[oldhash]

		if action != 'del':
			named = Vessel.Item(
								id=id(item), 
								name=name, 
								item=item, 
								typ=type(item),
								vessel=vessel
								)
			hash_str = self._hash_str(id(item), name, item)
			Vessel._hash_dict[self._hash(hash_str)] = named

		# update the __items list
		if vessel is not None:
			vessel.__items = BoxList([(v.id, v.name, v.item) 
								for v in Vessel._hash_dict.values()
								if v.vessel==vessel])
		
	@property
	def __ids(self):
		return BoxList([a[0] for a in self.__items])

	@property
	def name_contents(self):
		return BoxList([(a[1],a[2]) for a in self.__items])

	@property
	def names(self):
		return BoxList([a[1] for a in self.__items])

	@property
	def contents(self):
		return BoxList([a[2] for a in self.__items])

	def contains(self, item):
		return item in self.contents or item in self.names

	def _hash_str(self, *args):
		return ''.join(str(a) for a in args)

	def _hash(self, string):
		hashed = hashlib.sha256(string.encode()).hexdigest()
		return hashed

	def _is_duplicate(self, name, item):
		dup_name = False if name is None else name in self.names
		if dup_name:
			raise BoxDuplicateError('This name has been used')
		if id(item) in self.__ids or (name, item) in self.name_contents:
			raise BoxDuplicateError('This item has already been boxed')
		return False

	def _good_key(self, key):
		''' check key is correct '''
		if not self.isopen:
			if key is None:
				raise BoxLockError('Box is locked. Provide a key to unlock.')
			elif key != self.key:
				raise BoxKeyError('Wrong key.')
		return True

	def _type_check(self, item):
		''' check type is expected '''
		if self.__itype is not None:
			if not isinstance(item, self.__itype):
				raise BoxItemTypeError(f'item {item} must be of box type {self.__itype}')
		elif type(item) not in self._accepts:
			raise BoxItemTypeError(f'item {item} must be one of {self._accepts}')
		return True

	def _kw_check(self, kw, exp, typ):
		''' check requested keyword is of expected data type '''
		if not isinstance(kw, typ):
			raise BoxExceptionError(f'Expected {exp} of type {typ.__name__}')
		return True

	def _index_check(self, index):
		''' test requested index is in range '''
		if index < 0 or index > len(self.contents) - 1:
			raise BoxItemAccessError('Index out of range')
		return True

	def put(self, item, name=None, key=None):
		''' add to contents '''
		if self._good_key(key) and self._type_check(item):
			if type(item) in self._mutables:
				from copy import deepcopy
				item = deepcopy(item)
			if name is None:
				try: name = item.name # use pre-existing if available
				except: pass
			if not self._is_duplicate(name, item):
				try: item.name = name	# assign attribute
				except: pass # nb. 
				self.__update__('put', item, name)
				
	def __find__(self, **kwargs):
		''' locates item for fetch, use, destroy etc '''

		action = kwargs.get('action')
		name = kwargs.get('name')
		index = kwargs.get('index')
		item = kwargs.get('item')
		
		if not self.isopen:
			raise BoxLockError(Vessel.LOCKED_MSG)

		# try and retrieve the item
		if name is not None:
			if self._kw_check(name, 'name', str):
				item = [v[1] for v in self.name_contents if v[0]==name][0]
		elif index is not None:
			if self._kw_check(index, 'index', int):
				if self._index_check(index):
					name = self.name_contents[index][0]				
					item = self.name_contents[index][1]
		elif item is not None:
			if not self.contains(item):
				item = None

		if item is None:
			raise BoxItemAccessError(f'Box does not have requested item')
		else:
			if action in ['fetch', 'destroy']:
				hash_str = self._hash_str(id(item), name, item)
				self.__update__('del', item, name, oldhash=self._hash(hash_str))
			if action in ['fetch', 'use']: 
				return item

	def fetch(self, /, **kwargs):
		return self.__find__(action='fetch', **kwargs)

	def use(self, /, **kwargs):
		return self.__find__(action='use', **kwargs)

	def destroy(self, /, **kwargs):
		self.__find__(action='fetch', **kwargs)

	def lock(self, key:str=None):
		if key is None:
			raise BoxLockError('Provide a key to lock.')
		elif not isinstance(key, str):
			raise BoxLockError('Key must be string.')
		self.key = key
		self.isopen = False

	def open(self, key:str=None):
		if self._good_key(key):
			self.isopen = True

	@property
	def name(self):
		''' for Vessels only '''
		return self.__name

	@name.setter
	def name(self, name):
		# need to distinguish between vessel's name and names of its items
		# we use global hash_dict to check for uniqueness of name
		if name is not None:
			for v in Vessel._hash_dict.values():
				if v.name == name:
					raise BoxNameError('This name has been used')

		# retrieve any existing name; nb this won't exist yet at __init__
		try: 
			oldname = self.name # will fail at __init__; passes for name resets
			if oldname != name:
				hash_str = self._hash_str(id(self), oldname, self)
				self.__name = name
				self.__update__('reset', self, name, 
								oldhash=self._hash(hash_str))
			else:
				pass # no change required
		except: # for __init__
			self.__name = name	
			self.__update__('put', self, name)	

	def getname(self, item=None):
		''' for vessels and Python base objects '''
		# returns first matching object
		if issubclass(type(item), Vessel):
			if item is None:	# cases of Vessel.getname()
				return self.name
			else:				# case - Vessel.getname(item itsel a vessel)
				return item.name
		else:	
			# case - item is not a vessel
			return [a[1] for a in self.__items if a[2] == item][0]
		
	def setname(self, item, name, key=None):
		''' only for items without names '''
		if self._good_key(key):
			if name is not None and name in self.names:
				raise BoxDuplicateError('This name has been used')
			else:
				if issubclass(item.__class__, Vessel):
					hash_str = self._hash_str(id(item), item.name, item)
				else:
					oldname = self.getname(item)
					hash_str = self._hash_str(id(item), oldname, item)
				self.__update__('reset', item, name,
								oldhash=self._hash(hash_str))

	def empty(self, key=None):
		''' empty vessel '''
		if self._good_key(key):
			Vessel._hash_dict.clear()
			self.__items = BoxList()	
			
	@property
	def isempty(self):
		return self.contents == []

	def __str__(self):
		return 'Vessel' if self.name is None else self.name
	def __repr__(self):
		v = 'Vessel'
		return f'{v}()' if self.name is None else f"{v}(name='{self.name}')"

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