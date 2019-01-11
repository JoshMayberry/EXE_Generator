#Version: 3.0.0

import os
import sys
import glob

import cx_Freeze
from distutils.core import setup

import MyUtilities.common

if (__name__ == "__main__"):
	from utilities import Exe_Base
	from utilities import Utilities
	from utilities import data_files_zip
else:
	from .utilities import Exe_Base
	from .utilities import Utilities
	from .utilities import data_files_zip

#Required Modules
##py -m pip install
	# cx_Freeze

#Import User Modules
if (__name__ == "__main__"):
	sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))) #Allows to import from the parent directory

def clearDirectory(directory):
	def onerror(function, path, exc_info):
		"""An Error handler for shutil.rmtree.
		Modified code from Justin Peel on https://stackoverflow.com/questions/2656322/shutil-rmtree-fails-on-windows-with-access-is-denied
		"""

		if (not os.access(path, os.W_OK)):
			os.chmod(path, stat.S_IWUSR)
			function(path)
		else:
			raise

	#######################################

	shutil.rmtree(directory, ignore_errors = False, onerror = onerror)

#Controllers
def build(*args, **kwargs):
	return Controller(*args, **kwargs)

class Controller(Utilities):
	def __init__(self):
		"""Used to create a .exe file.
		For good module structure practices, see: http://blog.habnab.it/blog/2013/07/21/python-packages-and-you/
		Special thanks to Ned Deily for how to detect 32 bit vs 64 bit on https://stackoverflow.com/questions/6107905/which-command-to-use-for-checking-whether-python-is-64bit-or-32bit/12057504#12057504

		mainFile (str) - The name of the main .py file

		Example Input: Exe_CxFreeze("runMe")
		"""

		super().__init__()

		self.modules = set()
		self.data_files = set()
		self.modules_include = set()
		self.modules_exclude = set()
		self.data_files_compressed = set()

	#Properties
	@MyUtilities.common.makeProperty(default = "MyApp")
	class title():
		"""What the program is called."""

		def setter(self, value: str):
			self._title = value

		def getter(self):
			return self._title

	@MyUtilities.common.makeProperty(default = "runMe.exe")
	class shortcut_name():
		"""What the .exe file is called."""

		def setter(self, value: str):
			self._shortcut_name = self.ensure_filePath(value, ending = ".exe", checkExists = False)

		def getter(self):
			return self._shortcut_name

	@MyUtilities.common.makeProperty(default = None)
	class icon():
		"""What icon to use for the .exe file."""

		def setter(self, value: str):
			if (value):
				self._icon = os.path.realpath(self.ensure_filePath(value, ending = ".ico"))
			else:
				self._icon = ""

		def getter(self):
			return self._icon

	@MyUtilities.common.makeProperty(default = "unknown")
	class version():
		"""The version number for the .exe file's info."""

		def setter(self, value: str):
			self._version = value

		def getter(self):
			return self._version

	@MyUtilities.common.makeProperty(default = "unknown")
	class description():
		"""The description for the .exe file's info."""

		def setter(self, value: str):
			self._description = value

		def getter(self):
			return self._description

	@MyUtilities.common.makeProperty(default = "unknown")
	class author():
		"""The author for the .exe file's info."""

		def setter(self, value: str):
			self._author = value

		def getter(self):
			return self._author

	@MyUtilities.common.makeProperty(default = "unknown")
	class author_email():
		"""The author's email for the .exe file's info."""

		def setter(self, value: str):
			self._author_email = value

		def getter(self):
			return self._author_email

	@MyUtilities.common.makeProperty(default = "dist")
	class destination():
		"""The pathway for the destination folder.
		The destination folder does not need to exist.

		Warning: Any files with the same name as ones that are generated will be overwritten.
		Warning: All existing files in that directory will be fremoved first.
		"""

		def setter(self, value: str):
			self._destination = value

		def getter(self):
			return self._destination

	@MyUtilities.common.makeProperty(default = None)
	class preScript():
		"""A .py script that should run before the .exe does."""

		def setter(self, value: str):
			if (value):
				self._preScript = os.path.realpath(self.ensure_filePath(value, ending = ".py"))
			else:
				self._preScript = None

		def getter(self):
			return self._preScript

	@MyUtilities.common.makeProperty(default = False)
	class optimized():
		"""Determines how to package the files for the .exe."""

		def setter(self, value: str):
			self._optimized = value

		def getter(self):
			return self._optimized

	#User Functions
	def excludeModule(self, moduleName):
		"""Excluded the given module in the .exe.

		moduleName (str) - The name of the module to include

		Example Input: includeModule("numpy")
		"""

		self.modules_exclude.add(moduleName)

	def includeModule(self, moduleName):
		"""Includes the given module in the .exe.

		moduleName (str) - The name of the module to include

		Example Input: includeModule("pickle")
		"""

		self.modules.add(moduleName)

	def includeFile(self, filePath: str, *, recursive: bool = True, folder: str = "", compressed = True):
		"""Includes the given file in the .exe.

		filePath (str) - What file to include
			- If directoiry: Will include all files in that directory
			- If list: Will include all files in the list

		folder (str) - What folder to put the included file in

		Example Input("settings.ini")
		Example Input("resources", folder = "resources")
		Example Input("resources/*.ico", folder = "resources")
		"""

		container = self.data_files
		# if (compressed):
		# 	container = self.data_files_compressed
		# else:
		# 	container = self.data_files

		for _filePath in self.ensure_container(filePath):
			if (os.path.isfile(_filePath)):
				container.add((os.path.realpath(_filePath), folder))
				continue

			for item in glob.iglob(_filePath, recursive = recursive):
				container.add((item, folder))

	def create(self, *, include_cmd: bool = False, freshBuildDir = True):
		"""Creates the .exe file

		include_cmd (bool) - Determines if the cmd window is shown or not 
			- If True: The cmd window will come up, which can be used for debugging.
			- If False: No cmd window will come up. Erros are logged in a .txt in the same folder as the .exe file and with the same name as the .exe
		
		Example Input: create()
		Example Input: create(True)
		"""

		def yieldKwargs_console():
			nonlocal self, include_cmd

			if (include_cmd):
				yield "base", None
			else:
				yield "base", "Win32GUI"

			yield "icon", self.icon
			yield "initScript", self.preScript
			yield "targetName", self.shortcut_name

		def yieldKwargs_options():
			nonlocal self

			yield "build_exe", self.destination

			if (self.modules):
				yield "packages", list(self.modules)
			if (self.modules_exclude):
				yield "excludes", list(self.modules_exclude)
			# if (self.modules_include):
			# 	yield "includes", list(self.modules_include)
			if (self.data_files):
				yield "include_files", list(self.data_files)

			if (self.optimized):
				yield "zip_include_packages", "*"
				yield "zip_exclude_packages", ""

				yield "compressed", True
				yield "optimize", 2

		####################################

		if (freshBuildDir):
			clearDirectory(self.destination)

		print("Creating .exe file...")
		cx_Freeze.setup(
			name = self.title,
			author = self.author,
			version = self.version,
			description = self.description,
			author_email = self.author_email,
			options = {
				"build_exe": dict(yieldKwargs_options()),
			},
			executables = [cx_Freeze.Executable(**dict(yield_kwargs_console()))]
		)

if (__name__ == "__main__"):
	exe = build()
	exe.create()
