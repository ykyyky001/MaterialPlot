import sys
import importlib
from gc import collect as gccollect
from gc import disable as gcdisable
from gc import enable as gcenable

ModuleNames = ["GraphicsModule", "main", "DataModel"]

def reloadModules():
	gcdisable()
	for name in ModuleNames:
		if name in sys.modules:
			sys.modules.pop(name)

	for name in ModuleNames:
		importlib.import_module(name)
	gcenable()
	gccollect()
