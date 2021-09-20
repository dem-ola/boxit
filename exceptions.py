''' Exceptions '''
from dataclasses import dataclass
import dataclasses

class BoxExceptionError(Exception):
	pass
class BoxKeyAccessError(BoxExceptionError):
	pass
class BoxItemAccessError(BoxExceptionError):
	pass
class BoxItemTypeError(BoxExceptionError):
	pass
class BoxNameError(BoxExceptionError):
	pass
class BoxDuplicateError(BoxExceptionError):
	pass
class BoxLockedError(BoxExceptionError):
	pass
class BoxImplementationError(BoxExceptionError):
	pass





