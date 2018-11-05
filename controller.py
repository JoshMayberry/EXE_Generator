#Version: 3.0.0

import os
import sys
import shutil
import collections

import re
import abc
import uuid
import inspect

import Utilities as MyUtilities

#Required Modules
##py -m pip install
	# nsist
	# py2exe
	# cx_Freeze

##Required Software
	#Inno Setup: http://www.jrsoftware.org/isdl.php

#Import User Modules
if (__name__ == "__main__"):
	sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))) #Allows to import from the parent directory

#Global Variables
data_files_zip = []
absPath = re.sub("([^\\\\])[\\\\]([^\\\\])", r"\1/\2", os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

#Controllers
def build_py2Exe(*args, **kwargs):
	return Exe_Py2Exe(*args, **kwargs)

def build_cxFreeze(*args, **kwargs):
	return Exe_CxFreeze(*args, **kwargs)

def build_pynsist(*args, **kwargs):
	return Exe_Pynsist(*args, **kwargs)

def build_innoSetup(*args, **kwargs):
	return Exe_InnoSetup(*args, **kwargs)

class Utilities(MyUtilities.common.Ensure):
	@classmethod
	def ensure_filePath(cls, filePath, *, ending = None, raiseError = True, default = None):
		if (filePath is None):
			return default
			
		if ((ending is not None) and (not filePath.endswith(ending))):
			filePath += ending

		if (not os.path.exists(filePath)):
			if (raiseError):
				raise FileNotFoundError(filePath)
			return default
		return filePath

class Exe_Base(Utilities, metaclass = abc.ABCMeta):
	def __init__(self, mainFile, name = None, version = None, author = None, description = None):
		"""Used to create a .exe file.
		For good module structure practices, see: http://blog.habnab.it/blog/2013/07/21/python-packages-and-you/
		Special thanks to Ned Deily for how to detect 32 bit vs 64 bit on https://stackoverflow.com/questions/6107905/which-command-to-use-for-checking-whether-python-is-64bit-or-32bit/12057504#12057504

		mainFile (str) - The name of the main .py file

		Example Input: Exe_Base("runMe")
		"""
		
		self.options = {}
		self.options["optimize"] = 0
		self.options["excludes"] = []
		self.options["includes"] = []

		self.console = {}
		self.console["script"] = ""

		self.setInfoName(name)
		self.setInfoAuthor(author)
		self.setInfoVersion(version)
		self.setInfoDescription(description)
		self.data_files = []

		self.setMain(mainFile)

	def optimizeSize(self, excludeInterpreter = False, safer = False):
		"""Makes the overall program smaller.

		excludeInterpreter (bool) - If True: The Python interpreter will not be bundled
		safer (bool) - There are some things that some computers don't have. Enable this to include those redundancies

		Example Input: optimizeSize()
		"""

		print("Optimizing file size...")

		self.options["optimize"] = 2
		self.options["excludes"] = [
			'_ssl',
			'pyreadline', 
			#'locale', 'difflib', #Both of these are needed if you are importing your own modules
			'doctest', 
			'optparse', 'pickle', 'calendar', 'pdb',
			'unitest', #Exclude standard library
			'numpy', #numpy is HUGE. Try to avoid it if you can
			'tkinter',
			]

		# self.options["dll_excludes"] = ['tcl86t.dll', 'tk86t.dll'] #Tkinter
		# if (not safer):
		# 	self.options["dll_excludes"].append('msvcr71.dll')  # Exclude msvcr71

	def setDestination(self, filePath, freshDirectory = True):
		"""Sets the destination folder for the program files.
		The destination folder does not need to exist.
		Warning: Any files with the same name as ones that are generated will be overwritten.

		filePath (str) - The pathway for the destination folder

		Example Input: setDestination("myProgram")
		"""

		if ((not freshDirectory) or (not os.path.exists(filePath))):
			return

		def onerror(function, path, exc_info):
			"""An Error handler for shutil.rmtree.
			Modified code from Justin Peel on https://stackoverflow.com/questions/2656322/shutil-rmtree-fails-on-windows-with-access-is-denied
			"""

			import stat

			if (not os.access(path, os.W_OK)):
				os.chmod(path, stat.S_IWUSR)
				function(path)
			else:
				raise
		shutil.rmtree(filePath, ignore_errors = False, onerror = onerror)

	# @abc.abstractmethod
	def setName(self, *args, **kwargs):
		pass

	def setMain(self, fileName):
		"""Sets the file path to the main .py file.

		fileName (str) - The name for the main .py file

		Example Input: setMain("convertToExcel")
		"""

		if (not fileName.endswith(".py")):
			fileName += ".py"

		if (not os.path.exists(fileName)):
			raise FileNotFoundError(fileName)

		self.console["script"] = fileName

	# @abc.abstractmethod
	def setIcon(self, *args, **kwargs):
		pass

	def setInfoName(self, name = None):
		"""Sets the name for the .exe file's info

		name (str) - What the app is called

		Example Input: setInfoName("start")
		"""

		if (name is None):
			self.name = "MyApp"
		else:
			self.name = name

	def setInfoVersion(self, version = None):
		"""Sets the version number for the .exe file's info

		version (str) - The version number. Can be an int, float, or double.

		Example Input: setInfoVersion("1.0")
		"""

		if (version is None):
			self.version = "unknown"
		else:
			self.version = f"{version}"

	def setInfoDescription(self, description = None):
		"""Sets the icon for the .exe file's info

		description (str) - What the program is meant to do

		Example Input: setInfoDescription("Converts a .ias file to an excel sheet")
		"""

		if (description is None):
			self.description = "unknown"
		else:
			self.description = f"{description}"

	def setInfoAuthor(self, author = None):
		"""Sets the author for the .exe file's info

		author (str) - Who created the program

		Example Input: setInfoAuthor("Joshua Mayberry")
		"""

		if (author is None):
			self.author = "unknown"
		else:
			self.author = f"{author}"

	def addFile(self, myInput, outputFolder = "", buildName = None, module = False, keepFolders = True, insideZip = False, ignore = None):
		"""Adds an extra file to the overall program bundle.

		myInput (str)      - The path to the .icon file.
							 If a folder is provided, all items in that folder will be added
		outputFolder (str) - The name for the folder where the file will be located
		module (bool)      - If True: the input given is a path to a module, not a file name
		keepFolders (bool) - Determines how the folder structure will be inside the added file
			- If True: Will keep files in the folders they were in before
			- If False: Will put all files in one folder
			- If None: Will not look in sub-folders
		insideZip (bool)   - Determines how to include the given files if it is bundling things into library.zip
			- If True: Will put them inside 'library.zip'
			- If True: Will put them outside 'library.zip'
		ignore (str)      - If anything with this name is in the provided folder, it will ignore that object (will not look inside if it is a folder)
			- Can provide a list of strings too

		Example Input: addFile("resources/cte_icon3.ico", "resources")
		Example Input: addFile("RP2005.dll", insideZip = True)
		"""

		if (ignore == None):
			ignore = []
		elif (not isinstance(ignore, (list, tuple))):
			ignore = [ignore]

		def getFullPath(filePath):
			"""Returns the full path of the provided item."""
			nonlocal self, ignore

			if ((filePath in ignore) or (os.path.basename(filePath) in ignore)):
				return None

			if (".." in filePath):
				return re.sub("\.\.", absPath, filePath)
			return filePath

		def getContents(filePath):
			"""Returns the contents of the provided directory."""
			nonlocal self

			filePath = getFullPath(filePath)
			if (filePath == None):
				return []

			elif (os.path.isfile(filePath)):
				return [filePath]
			else:
				queue = []
				for item in os.listdir(filePath):
					queue.extend(getContents(os.path.join(filePath, item)))
				return queue

		################################################

		# print("Adding file(s)...")

		#Configure the list of documentation files
		if (type(myInput) == str):
			if (".." in myInput):
				myInput_abs = re.sub("\.\.", absPath, myInput)
			else:
				myInput_abs = None

			if (not module):
				# print("@0", myInput)
				#Determine contents
				outputContents = getContents(myInput)

			else:
				outputContents = [myInput]

			#Account for windows backslash escaping
			outputContents = [re.sub("([^\\\\])[\\\\]([^\\\\])", r"\1/\2", item) for item in outputContents]

			#Keep folder structure
			if (keepFolders != None):
				if (keepFolders):
					structure = {} #{destination folder: source contents} Example: {'database': ['database/labelContent.db']}; {'C:/Users/Josh/Documents/Python/modules/API_ExcelManipulator': ['C:/Users/Josh/Documents/Python/modules/API_ExcelManipulator/controller.py', 'C:/Users/Josh/Documents/Python/modules/API_ExcelManipulator/LICENSE', 'C:/Users/Josh/Documents/Python/modules/API_ExcelManipulator/version.py', 'C:/Users/Josh/Documents/Python/modules/API_ExcelManipulator/__init__.py']}

					#Discover the file structure
					for item in outputContents:
						if (os.path.isabs(item)):
							rootItem = re.sub(f"^{myInput_abs}[/\\\\]", "", item)
							rootItem = re.sub(f"^{myInput_abs}", "", rootItem)
						else:
							if (os.path.isfile(myInput)):
								rootItem = re.sub(f"^{os.path.dirname(myInput)}[/\\\\]", "", item)
								rootItem = re.sub(f"^{os.path.dirname(myInput)}", "", rootItem)
							else:
								rootItem = re.sub(f"^{myInput}[/\\\\]", "", item)
								rootItem = re.sub(f"^{myInput}", "", rootItem)

						folder = os.path.join(outputFolder, rootItem)

						if (folder not in structure):
							structure[folder] = []

						structure[folder].append(item)

					#Add file structure
					for folder, contents in structure.items():
						if (insideZip and self.options.get(zipOption)):
							data_files_zip.append((folder, contents))
						else:
							self.data_files.append((folder, contents))
				else:
					#Add all files
					if (self.options["compressed"] and insideZip):
						data_files_zip.append((outputFolder, outputContents))
					else:
						self.data_files.append((outputFolder, outputContents))
			else:
				#Only add the top level
				if (self.options["compressed"] and insideZip):
					data_files_zip.append((outputFolder, outputContents))
				else:
					self.data_files.append((outputFolder, outputContents))
		else:
			#Modules themselves are passed instead of the path to them
			outputContents = [myInput]

			if (self.options["compressed"] and insideZip):
				data_files_zip.append(outputContents)
			else:
				self.data_files.append(outputContents)

	def addInclude(self, moduleList, userModule = False):
		"""Adds a list of modules to the 'include this' list.
		Also makes sure that any dependant modules are included

		moduleList (list) - Modules to include in the overall bundle as strings

		Example Input: addInclude(["PIL", "numpy"])
		Example Input: addInclude("PIL")
		Example Input: addInclude("modules.GUI_Maker")
		"""

		#Ensure correct type
		if (type(moduleList) != list):
			moduleList = [moduleList]

		if (userModule):
			#Ensure nested modules are included too
			nestedModules = []
			for module in moduleList:
				exec(f"import {module}")
				modulePath = os.path.dirname(inspect.getfile(eval(module)))

				for item in inspect.getmembers(eval(module), inspect.ismodule):
					if (not item[0] in sys.builtin_module_names):
						nestedPath = inspect.getfile(item[1])
						if (not modulePath in nestedPath):
							nestedModules.append(item[1])

				# nestedModules.extend([item[0] for item in inspect.getmembers(eval(module), inspect.ismodule)])
			self.options["includes"].extend(nestedModules)
		else:
			self.options["includes"].extend(moduleList)

		#Remove duplicates
		self.options["includes"] = list(dict.fromkeys(self.options["includes"]))

		# #Remove private modules
		# self.options["includes"] = [item for item in self.options["includes"] if (item[0] != "_")]

	def addExclude(self, moduleList, dll = False):
		"""Adds a list of modules to the 'do not include this' list.

		moduleList (list) - Modules to not include in the overall bundle as strings
		dll (bool)        - Determines if it is a dll exclude or not

		Example Input: addExclude(["PIL", "numpy"])
		Example Input: addExclude("PIL")
		"""

		#Ensure correct type
		if (type(moduleList) == str):
			moduleList = [moduleList]

		if (dll):
			self.options["dll_excludes"].extend(moduleList)
		else:
			self.options["excludes"].extend(moduleList)

	@abc.abstractmethod
	def create(self, *args, **kwargs):
		pass

class Exe_Py2Exe(Exe_Base):
	def __init__(self, *args, **kwargs):
		"""Used to create a .exe file.
		For good module structure practices, see: http://blog.habnab.it/blog/2013/07/21/python-packages-and-you/
		Special thanks to Ned Deily for how to detect 32 bit vs 64 bit on https://stackoverflow.com/questions/6107905/which-command-to-use-for-checking-whether-python-is-64bit-or-32bit/12057504#12057504

		mainFile (str) - The name of the main .py file

		Example Input: Exe_Py2Exe("runMe")
		"""

		import py2exe
		import zipfile
		from distutils.core import setup

		self.original_copy_files = py2exe.runtime.Runtime.copy_files
		py2exe.runtime.Runtime.copy_files = self.better_copy_files

		sys.argv.append('py2exe')

		super().__init__(*args, **kwargs)
		
		self.options["compressed"] = False
		self.options["dist_dir"] = "dist"
		self.options["skip_archive"] = True
		self.options["dll_excludes"] = []
		self.options["bundle_files"] = 3

		self.console["icon_resources"] = [],
		self.console["dest_base"] = "runMe",

	def better_copy_files(self, destdir):
		"""Overriden so that things can be included in the library.zip."""
		
		#Run function as normal
		original_copy_files(self, destdir)

		#Get the zipfile's location
		if self.options.libname is not None:
			libpath = os.path.join(destdir, self.options.libname)

			#Re-open the zip file
			if self.options.compress:
				compression = zipfile.ZIP_DEFLATED
			else:
				compression = zipfile.ZIP_STORED
			arc = zipfile.ZipFile(libpath, "a", compression = compression)

			#Add your items to the zipfile
			for folder in data_files_zip:
				for item in folder[1]:
					#Account for folders
					newPath = os.path.join(folder[0], os.path.basename(item))

					if self.options.verbose:
						print("Copy File %s to %s as %s" % (item, libpath, newPath))
					arc.write(item, newPath)
			arc.close()

	def optimizeSize(self, *args, **kwargs):
		"""Makes the overall program smaller.

		excludeInterpreter (bool) - If True: The Python interpreter will not be bundled
		safer (bool) - There are some things that some computers don't have. Enable this to include those redundancies

		Example Input: optimizeSize()
		"""

		super().optimizeSize(*args, **kwargs)

		self.options["compressed"] = True  # Compress library.zip
		# self.options["bundle_files"] = 0 #Bundle everything
		# self.options["bundle_files"] = 1 #Bundle everything but dlls
		self.options["bundle_files"] = 2 #Bundle everything but the interpreter and dlls


	def setDestination(self, filePath, *args, **kwargs):
		"""Sets the destination folder for the program files.
		The destination folder does not need to exist.
		Warning: Any files with the same name as ones that are generated will be overwritten.

		filePath (str) - The pathway for the destination folder

		Example Input: setDestination("myProgram")
		"""

		self.options["dist_dir"] = filePath

		super().setDestination(filePath, *args, **kwargs)

	def setName(self, fileName):
		"""Sets the name of the .exe file.

		fileName (str) - The name for the .exe file

		Example Input: setName("convertToExcel")
		"""

		self.console["dest_base"] = fileName

	def setIcon(self, fileName):
		"""Sets the icon for the .exe file

		fileName (str) - The path to the .icon file

		Example Input: setIcon("resources/cte_icon3")
		"""

		self.console["icon_resources"] = [(0, fileName + ".ico")]

	def addFile(self, *args, **kwargs):
		"""Adds an extra file to the overall program bundle.

		myInput (str)      - The path to the .icon file.
							 If a folder is provided, all items in that folder will be added
		outputFolder (str) - The name for the folder where the file will be located
		module (bool)      - If True: the input given is a path to a module, not a file name
		keepFolders (bool) - Determines how the folder structure will be inside the added file
			- If True: Will keep files in the folders they were in before
			- If False: Will put all files in one folder
			- If None: Will not look in sub-folders
		insideZip (bool)   - Determines how to include the given files if it is bundling things into library.zip
			- If True: Will put them inside 'library.zip'
			- If True: Will put them outside 'library.zip'
		ignore (str)      - If anything with this name is in the provided folder, it will ignore that object (will not look inside if it is a folder)
			- Can provide a list of strings too

		Example Input: addFile("resources/cte_icon3.ico", "resources")
		Example Input: addFile("RP2005.dll", insideZip = True)
		"""

		super().addFile(*args, zipOption = "compressed", **kwargs)

	def moduleExceptions(self, module):
		"""Checks for specific modules that are loaded and then takes action to make them work properly.

		module (str) - The name of a module you want checked

		Example Input: moduleExceptions("matplotlib")
		Example Input: moduleExceptions("win32com")
		Example Input: moduleExceptions("tkinter")
		"""

		print("Checking for module exceptions...")

		#Ensure correct format
		module = module.lower()

		#Import the module so that the modules within can be assessed

		#Check the modules for key modules that need special attention
		##win32com
		if ((module == "win32com") or (module == "excelmanipulator")):
			#The pickle module is needed. This is usually excluded upon optimization
			try:
				self.options["excludes"].remove("pickle")
				print("win32com needs pickle to work")
			except:
				pass

			#Because of how windows COM handles things, the COM cannot be bundled
			if (self.options["bundle_files"] != 3):
				print("Modules using win32com cannot be bundled.")
				self.options["bundle_files"] = 3

		##matplotlib
		if ((module == "matplotlib") or (module == "plt")):
			try:
				self.options["excludes"].remove("numpy")
				print("matplotlib needs numpy to work")
			except:
				pass

			try:
				self.options["excludes"].remove("difflib")
				print("matplotlib needs difflib to work")
			except:
				pass

			try:
				self.options["excludes"].remove("locale")
				print("matplotlib needs locale to work")
			except:
				pass

			try:
				self.options["excludes"].remove("pickle")
				print("matplotlib needs pickle to work")
			except:
				pass

			try:
				self.options["excludes"].remove("calendar")
				print("matplotlib needs calendar to work")
			except:
				pass

	def create(self, include_cmd = False):
		"""Creates the .exe file

		include_cmd (bool) - Determines if the cmd window is shown or not 
								~ If True: The cmd window will come up, which can be used for debugging.
								~ If False: No cmd window will come up. Erros are logged in a .txt in the same folder as the .exe file and with the same name as the .exe
		Example Input: create()
		Example Input: create(True)
		"""

		print("Creating .exe file...")

		if (include_cmd):
			setup(name = self.name,
				version = self.version,
				description = self.description,
				author = self.author,
				data_files = self.data_files,
				console = [self.console],
				options = {'py2exe': self.options},
				)
		else:
			setup(name = self.name,
				version = self.version,
				description = self.description,
				author = self.author,
				data_files = self.data_files,
				windows = [self.console],
				options = {'py2exe': self.options},
				)

class Exe_CxFreeze(Exe_Base):
	def __init__(self, *args, **kwargs):
		"""Used to create a .exe file.
		For good module structure practices, see: http://blog.habnab.it/blog/2013/07/21/python-packages-and-you/
		Special thanks to Ned Deily for how to detect 32 bit vs 64 bit on https://stackoverflow.com/questions/6107905/which-command-to-use-for-checking-whether-python-is-64bit-or-32bit/12057504#12057504

		mainFile (str) - The name of the main .py file

		Example Input: Exe_CxFreeze("runMe")
		"""

		import cx_Freeze
		from distutils.core import setup

		super().__init__(*args, **kwargs)
		
		self.options["build_exe"] = "dist"
		
		self.console["icon"] = ""
		self.console["initScript"] = None
		self.console["targetName"] = "runMe.exe"

	def optimizeSize(self, *args, **kwargs):
		"""Makes the overall program smaller.

		excludeInterpreter (bool) - If True: The Python interpreter will not be bundled
		safer (bool) - There are some things that some computers don't have. Enable this to include those redundancies

		Example Input: optimizeSize()
		"""

		super().optimizeSize(*args, **kwargs)

		self.options["zip_include_packages"] = "*"
		self.options["zip_exclude_packages"] = ""

	def setDestination(self, filePath, *args, **kwargs):
		"""Sets the destination folder for the program files.
		The destination folder does not need to exist.
		Warning: Any files with the same name as ones that are generated will be overwritten.

		filePath (str) - The pathway for the destination folder

		Example Input: setDestination("myProgram")
		"""

		self.options["build_exe"] = filePath

		super().setDestination(filePath, *args, **kwargs)

	def setName(self, fileName):
		"""Sets the name of the .exe file.

		fileName (str) - The name for the .exe file

		Example Input: setName("convertToExcel")
		"""

		self.console["targetName"] = f"{fileName}.exe"

	def setIcon(self, fileName):
		"""Sets the icon for the .exe file

		fileName (str) - The path to the .icon file

		Example Input: setIcon("resources/cte_icon3")
		"""

		self.console["icon"] = fileName + ".ico"

	def addFile(self, *args, **kwargs):
		"""Adds an extra file to the overall program bundle.

		myInput (str)      - The path to the .icon file.
							 If a folder is provided, all items in that folder will be added
		outputFolder (str) - The name for the folder where the file will be located
		module (bool)      - If True: the input given is a path to a module, not a file name
		keepFolders (bool) - Determines how the folder structure will be inside the added file
			- If True: Will keep files in the folders they were in before
			- If False: Will put all files in one folder
			- If None: Will not look in sub-folders
		insideZip (bool)   - Determines how to include the given files if it is bundling things into library.zip
			- If True: Will put them inside 'library.zip'
			- If True: Will put them outside 'library.zip'
		ignore (str)      - If anything with this name is in the provided folder, it will ignore that object (will not look inside if it is a folder)
			- Can provide a list of strings too

		Example Input: addFile("resources/cte_icon3.ico", "resources")
		Example Input: addFile("RP2005.dll", insideZip = True)
		"""

		super().addFile(*args, zipOption = "zip_include_", **kwargs)

	def addExclude(self, moduleList, dll = False):
		"""Adds a list of modules to the 'do not include this' list.

		moduleList (list) - Modules to not include in the overall bundle as strings
		dll (bool)        - Determines if it is a dll exclude or not

		Example Input: addExclude(["PIL", "numpy"])
		Example Input: addExclude("PIL")
		"""

		#Ensure correct type
		if (type(moduleList) == str):
			moduleList = [moduleList]

		self.options["excludes"].extend(moduleList)

	def create(self, include_cmd = False):
		"""Creates the .exe file

		include_cmd (bool) - Determines if the cmd window is shown or not 
								~ If True: The cmd window will come up, which can be used for debugging.
								~ If False: No cmd window will come up. Erros are logged in a .txt in the same folder as the .exe file and with the same name as the .exe
		Example Input: create()
		Example Input: create(True)
		"""

		def fixDataFiles():
			"""Fixes the data files for cx_Freeze."""
			nonlocal self

			#Datafile fix
			newData_files = []
			for destination, sourceList in self.data_files:
				for source in sourceList:
					if (os.path.isfile(source)):
						newData_files.append((source, destination))
					else:
						newData_files.append((source, os.path.join(destination, os.path.basename(source))))

			self.data_files = newData_files[:]

			#Zip fix
			for item in data_files_zip:
				iouiuio

			# print("@5", self.data_files)

		########################################

		print("Creating .exe file...")

		sys.argv.append('build')

		if (include_cmd):
			self.console["base"] = None
		else:
			self.console["base"] = "Win32GUI"

		print("@1", self.options)
		print("@2", self.console)

		exe = cx_Freeze.Executable(**self.console)

		# if ("compressed" in self.options):
		# 	del self.options["compressed"]

		fixDataFiles()

		print("@3", self.data_files)

		self.options["include_files"] = self.data_files

		cx_Freeze.setup(
			name = self.name,
			version = self.version,
			description = self.description,
			author = self.author,
			author_email = "",
			options = {"build_exe": self.options},
			executables = [exe]
		)

class Exe_Pynsist(Exe_Base):
	def __init__(self, mainFile):
		"""Used to create a .exe file.
		For good module structure practices, see: http://blog.habnab.it/blog/2013/07/21/python-packages-and-you/
		Special thanks to Ned Deily for how to detect 32 bit vs 64 bit on https://stackoverflow.com/questions/6107905/which-command-to-use-for-checking-whether-python-is-64bit-or-32bit/12057504#12057504

		mainFile (str) - The name of the main .py file

		Example Input: Exe_Pynsist("runMe")
		"""

		import site
		import glob
		import modulefinder

		# import nsist
		import forks.pynsist.nsist as nsist #Use my own fork

		super().__init__(mainFile)

		self.options["build_dir"] = "dist"
		self.options["license_file"] = None
		self.options["py_version"] = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
		self.options["py_bitness"] = 64 if (sys.maxsize > 2**32) else 32
		self.options["extra_installers"] = []
		
		self.console["icon"] = ""
		self.console["publisherName"] = None #The publisher name that shows up in the Add or Remove programs control panel.
		self.console["installerName"] = "myInstaller"

	def setName(self, name = None):
		self.console["installerName"] = name or "myInstaller"

	def optimizeSize(self, *args, **kwargs):
		"""Does not use"""

		return

	def setDestination(self, filePath, *args, **kwargs):
		"""Sets the destination folder for the program files.
		The destination folder does not need to exist.
		Warning: Any files with the same name as ones that are generated will be overwritten.

		filePath (str) - The pathway for the destination folder

		Example Input: setDestination("myProgram")
		"""

		self.options["build_dir"] = filePath

		super().setDestination(filePath, *args, **kwargs)

	def setIcon(self, fileName):
		"""Sets the icon for the .exe file

		fileName (str) - The path to the .icon file

		Example Input: setIcon("resources/cte_icon3")
		"""
		
		self.console["icon"] = fileName + ".ico"

	def addFile(self, myInput, outputFolder = "", buildName = None, module = False, keepFolders = True, insideZip = False, ignore = None):
		"""Adds an extra file to the overall program bundle.

		myInput (str)      - The path to the .icon file.
							 If a folder is provided, all items in that folder will be added
		outputFolder (str) - The name for the folder where the file will be located
		module (bool)      - If True: the input given is a path to a module, not a file name
		keepFolders (bool) - Determines how the folder structure will be inside the added file
			- If True: Will keep files in the folders they were in before
			- If False: Will put all files in one folder
			- If None: Will not look in sub-folders
		insideZip (bool)   - Determines how to include the given files if it is bundling things into library.zip
			- If True: Will put them inside 'library.zip'
			- If True: Will put them outside 'library.zip'
		ignore (str)      - If anything with this name is in the provided folder, it will ignore that object (will not look inside if it is a folder)
			- Can provide a list of strings too

		Example Input: addFile("resources/cte_icon3.ico", "resources")
		Example Input: addFile("RP2005.dll", insideZip = True)
		"""

		if (ignore == None):
			ignore = []
		elif (not isinstance(ignore, (list, tuple))):
			ignore = [ignore]

		def getFullPath(filePath):
			"""Returns the full path of the provided item."""
			nonlocal self, ignore

			if ((filePath in ignore) or (os.path.basename(filePath) in ignore)):
				return None

			if (".." in filePath):
				return re.sub("\.\.", absPath, filePath)
			return filePath

		################################################

		if (not os.path.isabs(outputFolder)):
			outputFolder = f"$INSTDIR/{outputFolder}"

		_myInput = getFullPath(myInput)

		if (buildName):
			self.data_files.append((_myInput, outputFolder, buildName))
		else:
			self.data_files.append((_myInput, outputFolder))

	def addInstaller(self, filePath, message = None, installType = None, condition = None):
		"""Adds an installer to be installed as well."""

		self.options["extra_installers"].append((filePath, message, installType, condition))

	def create(self, include_cmd = False):
		"""Creates the .exe file

		include_cmd (bool) - Determines if the cmd window is shown or not 
								~ If True: The cmd window will come up, which can be used for debugging.
								~ If False: No cmd window will come up. Erros are logged in a .txt in the same folder as the .exe file and with the same name as the .exe
		Example Input: create()
		Example Input: create(True)
		"""

		print("Creating .exe installer...")

		#Find all needed packages
		finder = modulefinder.ModuleFinder()
		finder.run_script(self.console["script"])

		packages = set()
		packages_ignorePath = {}
		packages_extraPath = {}
		sitePackageDirectory = site.getsitepackages()[1]
		for name in finder.modules.keys():
			if (("." not in name) and (not name.startswith("_")) and (name not in self.options["excludes"])):
				if (name in ["ObjectListView"]):
					continue #Prevent duplicate entries
				if ((os.path.exists(os.path.join(sitePackageDirectory, name))) or (os.path.exists(os.path.join(sitePackageDirectory, f"{name}.py")))):
					packages.add(name)
				elif ((glob.glob(os.path.join(sitePackageDirectory, f"{name}*.dist-info"))) or (glob.glob(os.path.join(sitePackageDirectory, f"{name}*.egg-info")))):
					packages.add(name)

		packages_extraPath["H:/Python/modules/forks/"] = "forks"
		if ("pynsist" in packages):
			packages_ignorePath["pynsist"] = ("H:/Python/modules/forks/pynsist/nsist/tests", "H:/Python/modules/forks/pynsist/.git", "H:/Python/modules/forks/pynsist/__pycache__")

		# packages = [name for name in finder.modules.keys() if (("." not in name) and (not name.startswith("_")) and (name not in self.options["excludes"]) and 
		# 	(os.path.exists(os.path.join(site.getsitepackages()[1], name))) or (os.path.exists(os.path.join(site.getsitepackages()[1], f"{name}.py"))))]
		print("@5.1", packages)
		print("@5.2", packages_extraPath)
		print("@5.3", packages_ignorePath)

		# for item in self.data_files:
		# 	print("@6", item)
		# jkhkjhjkhjkj

		#Create builder
		builder = nsist.InstallerBuilder(self.name,
			self.version,
			{self.name: 
				{"script": self.console["script"],
				"console": include_cmd,
				"icon": self.console["icon"]
				}
			},
			publisher = None, #self.console["publisherName"],
			icon = self.console["icon"],
			packages = list(packages) + self.options["includes"],
			packages_extraPath = packages_extraPath,
			packages_ignorePath = packages_ignorePath,
			extra_files = self.data_files,
			py_version = self.options["py_version"],
			py_bitness = self.options["py_bitness"],
			build_dir = self.options["build_dir"],
			installer_name = None, #self.console["installerName"],
			exclude = self.options["excludes"],
			license_file = self.options["license_file"],
			extra_installers = self.options["extra_installers"],
			
			nsi_template = None,
			extra_wheel_sources = None,
			pypi_wheel_reqs = None,
			py_format = 'bundled',
			inc_msvcrt = True,
			commands = None,
			)

		builder.run()

class Exe_InnoSetup(Utilities):
	"""Install Inno Setup at: http://www.jrsoftware.org/isdl.php"""

	def __init__(self, **kwargs):
		"""Helps create an inno setup installer.

		innoSetup_installDir (str) - Where Inno Setup was installed to

		Exe_InnoSetup("runMe")
		"""

		self.shortcutCatalogue = {}

		for variable, value in kwargs.items():
			setattr(self, variable, value)

	@classmethod
	def withoutSpaces(cls, value):
		return re.sub("\s", "_", value)

	#App Information Properties
	@MyUtilities.common.lazyProperty()
	def uuid(self, value):
		"""Changes the uuid for the program."""

		return value or uuid.uuid4()

	@MyUtilities.common.lazyProperty()
	def version(self, value, *, default = "unknown"):
		"""What version the program is."""
		
		return value or default

	@MyUtilities.common.lazyProperty()
	def publisher(self, value, *, default = None):
		"""Who the publisher is."""
		
		return value or default

	@MyUtilities.common.lazyProperty()
	def publisherWebsite(self, value, *, default = None):
		"""The publisher's url."""
		
		return value or default

	@MyUtilities.common.lazyProperty()
	def supportWebsite(self, value, *, default = None):
		"""The support url."""
		
		return value or default

	@MyUtilities.common.lazyProperty()
	def supportPhone(self, value, *, default = None):
		"""The support phone number."""
		
		return value or default

	@MyUtilities.common.lazyProperty()
	def updateWebsite(self, value, *, default = None):
		"""The updates url."""
		
		return value or default

	@MyUtilities.common.lazyProperty()
	def readmeWebsite(self, value, *, default = None):
		"""The readme url."""
		
		return value or default

	@MyUtilities.common.lazyProperty()
	def preInfoPage(self, value, *, default = None):
		"""The a text file that will be displayed as a wizard page before the user selects where to install the app."""
		
		return value or default

	@MyUtilities.common.lazyProperty()
	def postInfoPage(self, value, *, default = None):
		"""The a text file that will be displayed as a wizard page after a sucessful install."""
		
		return value or default

	#Installer Properties
	@MyUtilities.common.lazyProperty()
	def defaultDir(self, value):
		"""Changes the default install directory for the installer."""
		
		return self.withoutSpaces(value or self.name)

	@MyUtilities.common.lazyProperty()
	def startMenuDir(self, value):
		"""Changes the default start menu folder for the created .exe."""
		
		return self.withoutSpaces(value or self.name)

	@MyUtilities.common.lazyProperty()
	def canCancel(self, value, *, default = True):
		"""Determines if the user can cancel the install or not."""
		
		if (value is None):
			return None
		if (value):
			return 1
		return 0

	@MyUtilities.common.lazyProperty()
	def canRestart(self, value, *, default = True):
		"""Determines if the program can show a restart message at the end of the installation if one is needed."""
		
		if (value is None):
			return None
		if (value):
			return 1
		return 0

	@MyUtilities.common.lazyProperty()
	def skip_startupMessage(self, value, *, default = True):
		"""Determines if a message asking if the user wants to install this before running the installer."""
		
		if (value is None):
			return None
		if (value):
			return 1
		return 0

	@MyUtilities.common.lazyProperty()
	def skip_welcomePage(self, value, *, default = True):
		"""Determines if the installer's welcome page should be shown or not."""
		
		if (value is None):
			return None
		if (value):
			return 1
		return 0

	@MyUtilities.common.lazyProperty()
	def update_fileAssociations(self, value, *, default = True):
		"""Determines file associations are updated upon install and uninstall."""
		
		if (value is None):
			return None
		if (value):
			return 1
		return 0

	@MyUtilities.common.lazyProperty()
	def update_environment(self, value, *, default = True):
		"""Determines environment variables are updated upon install and uninstall."""
		
		if (value is None):
			return None
		if (value):
			return 1
		return 0

	@MyUtilities.common.lazyProperty()
	def closeApps(self, value, *, default = False):
		"""Determines what happens if the installer needs to modify a file that is being used by another program.
			- If None: Will try using them anyways
			- If True: Will try forcing those apps to close before continuing
			- If False: Will ask if those apps should be closed before continuing
		"""
		
		if (value is None):
			return 0
		if (value):
			return "force"
		return 1

	@MyUtilities.common.lazyProperty()
	def restartApps(self, value, *, default = None):
		"""Determines what happens once the installer is finished if the installer has closed an application.
			- If True: Will try restarting closed applications
			- If False: Nothing
			- If None: Nothing
		"""
		
		if (value is None):
			return None
		if (value):
			return 1
		return 0

	@MyUtilities.common.lazyProperty()
	def forceLogging(self, value, *, default = None):
		"""Determines if a log file (from the install?) will always be created or not."""
		
		if (value is None):
			return None
		if (value):
			return 1
		return 0

	@MyUtilities.common.lazyProperty()
	def windows_minVersion(self, value, *, default = None):
		"""What the minimum windows version the installer will work for.
		Must be greater than 5.0

		5.0.2195 - Windows 2000 
		5.1.2600 - Windows XP or Windows XP 64-Bit Edition Version 2002 (Itanium) 
		5.2.3790 - Windows Server 2003 or Windows XP x64 Edition (AMD64/EM64T) or Windows XP 64-Bit Edition Version 2003 (Itanium) 
		6.0.6000 - Windows Vista 
		6.0.6001 - Windows Vista with Service Pack 1 or Windows Server 2008 
		6.1.7600 - Windows 7 or Windows Server 2008 R2 
		6.1.7601 - Windows 7 with Service Pack 1 or Windows Server 2008 R2 with Service Pack 1 
		6.2.9200 - Windows 8 or Windows Server 2012 
		6.3.9200 - Windows 8.1 or Windows Server 2012 R2 
		6.3.9600 - Windows 8.1 with Update 1 
		10.0.10240 - Windows 10 Version 1507 
		10.0.10586 - Windows 10 Version 1511 (November Update) 
		10.0.14393 - Windows 10 Version 1607 (Anniversary Update) 
		10.0.15063 - Windows 10 Version 1703 (Creators Update) 
		10.0.16299 - Windows 10 Version 1709 (Fall Creators Update) 
		10.0.17134 - Windows 10 Version 1803 (April 2018 Update) 


		Example Use:
			windows_minVersion = 10.0
			windows_minVersion = 5.0.2195
			windows_minVersion = 5.0sp4
			windows_minVersion = 5.0.2195sp4
		"""
		
		answer = value or default
		if (answer is None):
			return None

		check = f"{answer}".split(".")
		if ((len(check) < 2) or (int(check[0]) < 5)):
			errorMessage = f"Invalid windows version {answer}"
			raise KeyError(errorMessage)

		return answer

	@MyUtilities.common.lazyProperty()
	def windows_maxVersion(self, value, *, default = None):
		"""What the maximum windows version the installer will work for."""
		
		answer = value or default
		if (answer is None):
			return None

		return answer

	#Uninstaller Properties
	@MyUtilities.common.lazyProperty()
	def regkey_uninstall(self, value, *, default = True):
		"""Determines a registry key should be created for the uninstaller or not."""
		
		if (value):
			return 1
		return 0

	#Directory Properties
	@MyUtilities.common.lazyProperty()
	def innoSetup_installDir(self, value, *, default = "C:/Program Files (x86)/Inno Setup 5"):
		"""Where Inno Setup is installed."""
	
		return value or default

	@MyUtilities.common.lazyProperty()
	def manifest(self, value, *, default = None):
		"""Where to place the output manifest file."""
		
		return value or default

	@MyUtilities.common.lazyProperty()
	def setupFile(self, value, *, default = "H:/Python/modules/API_Exe/default_setup.iss"):
		"""Where the setup file is located"""
		
		return self.ensure_filePath(value, ending = ".iss", default = default)

	@MyUtilities.common.lazyProperty()
	def pythonPath(self, value, *, default = "\\\\dmte3\\MaterialDB\\Python36\\"):
		"""Where pythonw.exe is installed at."""
		
		return self.ensure_filePath(value, ending = "python.exe", default = default)

	@MyUtilities.common.lazyProperty()
	def script(self, value, *, default = None):
		"""Where the script is located."""
		
		return value# self.ensure_filePath(value, ending = ".py", default = default)

	@MyUtilities.common.lazyProperty()
	def dirExistsWarning(self, value, *, default = False):
		"""Determines what happens if the user selects a directory that already exists.
			- If None: Will never show a warning
			- If True: Will always show a warning
			- If False: Will only show a warning if another version of the same app is already installed there
		"""
		
		if (value is None):
			return 0
		if (value):
			return 1
		return "auto"

	#Icon Properties
	@MyUtilities.common.lazyProperty()
	def icon_installer(self, value):
		"""What icon the installer has."""
		
		return self.ensure_filePath(value, ending = ".ico", default = self.icon)

	@MyUtilities.common.lazyProperty()
	def icon(self, value, *, default = None):
		"""What icon the generated .exe file has."""
		
		return self.ensure_filePath(value, ending = ".ico", default = default)

	@MyUtilities.common.lazyProperty()
	def icon_desktop_state(self, value, *, default = True):
		"""Determines if an icon can be placed on the desktop.
			- If None: Do not give the option
			- If True: Check the box by default
			- If False: Do not check the box by default

		See: Tasks -> Flags
		"""

		if (value is None):
			value = default

		if (value is None):
			return "unchecked" #For now...
		if (value):
			return "exclusive"
		return "unchecked"

	@MyUtilities.common.lazyProperty()
	def icon_desktop_name(self, value):
		"""What the icon on the desktop should say.
			- If None: Will use the app's name
		"""
	
		return self.withoutSpaces(value or self.name)

	#Functions
	def optimize(self):
		"""Use the following sections from Inno Setup Help:
			- Setup -> Compression
			- Setup -> CompressionThreads
			- Setup -> LZMA*
			- Setup -> MergeDuplicateFiles
			- Setup -> SetupMutex
			- Setup -> AppMutex
			- Setup -> SolidCompression

		"""

		raise NotImplementedError()

	def autoStart(self):
		"""Use the following sections from Inno Setup Help:
			- Setup -> DisableFinishedPage
			- Run -> nowait

		"""

		raise NotImplementedError()

	def encrypt(self):
		"""Use the following sections from Inno Setup Help:
			- Setup -> Password
			- Setup -> Encryption

		"""

		raise NotImplementedError()

	def language(self):
		"""Use the following sections from Inno Setup Help:
			- Setup -> LanguageDetectionMethod
			- Setup -> ShowLanguageDialog
			- Setup -> ShowUndisplayableLanguages
			- Language -> *

		"""

		raise NotImplementedError()

	def legal(self):
		"""Use the following sections from Inno Setup Help:
			- Setup -> LicenseFile
			- Setup -> VersionInfo*

		"""

		raise NotImplementedError()

	def uninstall(self):
		"""Use the following sections from Inno Setup Help:
			- Setup -> Uninstall*

		"""

		raise NotImplementedError()

	def update_or_modify(self):
		"""Use the following sections from Inno Setup Help:
			- Setup -> UpdateUninstallLogAppName

		"""

		raise NotImplementedError()

	def userInfo(self):
		"""Use the following sections from Inno Setup Help:
			- Setup -> UserInfoPage

		"""

		raise NotImplementedError()

	def etc(self):
		"""Use the following sections from Inno Setup Help:
			- Setup -> Sign Tool
			- Setup -> SourceDir
			- Setup -> PrivilegesRequired; UsedUserAreasWarning
			- Setup -> TerminalServicesAware
			- Setup -> TouchDate
			- Setup -> TouchTime
			- Setup -> UsePrevious*
			- Setup -> WizardImage*

		"""

		raise NotImplementedError()

	def yieldShortcut(self, source, name = None, icon = None, 
		destination = None, workingDir = None, params = None):
		"""Yields variables pertaining to the shortcut.

		source (str) - What file the icon will run

		name (str) - What the shortcut will say
			- If None: Will use the app name

		icon (str) - Where the icon file is located
			- If None: Uses the installer's icon file

		destination (str) - What subfolder 'source' will be located in after the install
			- If None: 'source' will be in the root directory

		workingDir (str) - Which directory to run the file in
			- If None: Uses the directory the shortcut is in

		params (tuple) - A list of cmd line params to run the file with
			- If None: No params will be given
		"""

		yield "source", source
		yield "name", name or self.name

		_icon = icon or self.icon
		yield "icon_source", _icon
		yield "icon", f"{{app}}\\{os.path.basename(_icon)}"
		
		yield "workingDir", workingDir or "{app}"

		if (destination is None):
			_destination = "{app}"
		else:
			_destination = f"{{app}}\\{destination}"
		yield "destination", _destination

		yield "isPython", source.endswith(".py")
		yield "script", os.path.join(_destination, os.path.basename(source))
		yield "params", ' '.join(re.sub('"', '""', item) for item in self.ensure_container(params))

	def setDesktop(self, *args, **kwargs):
		"""Adds a shortcut to the desktop."""

		self.shortcutCatalogue["shortcutDesktop"] = lambda: self.yieldShortcut(*args, **kwargs)

	def setStartMenu(self, *args, **kwargs):
		"""Adds a shortcut to the start menu."""

		self.shortcutCatalogue["shortcutStartMenu"] = lambda: self.yieldShortcut(*args, **kwargs)

	def create(self, outputDir = None, *, quiet = None, issFile = None, **innoVars):
		"""Passes the inno setup file to the compiler.
			How to pass preProcessor commands in a cmd: 
				Inno Setup -> Help -> Inno Setup Preprocessor -> Other Information -> Extend Command Line Compiler

			outputDir (str) - Where to save the install file

			quiet (bool) - Determines if messages are printed to the cmd window
				- If None: All messages will be shown
				- If True: Only error messages will be shown
				- If False: Both progress and error messages will be shown

			innoVars (any) - Extra values that will be passed to the .iss file

		Example Input: create()
		"""

		def yieldSwitches():
			nonlocal outputDir, quiet, innoVars

			if (outputDir is not None):
				yield f"/O{outputDir}"

			if (quiet is not None):
				if (quiet):
					yield "/Q"
				else:
					yield "/Qp"


			for variable, value in innoVars.items():
				if (value is None):
					continue
				yield f"/D{variable}={value}"

			for label, shortcut in self.shortcutCatalogue.items():
				for variable, value in shortcut():
					yield f"/D{label}_{variable}={value}"

		####################################

		for variable in _lazyProperties_all[self.__class__.__name__]:
			innoVars.setdefault(variable, getattr(self, variable))

		import subprocess
		args = [
			os.path.join(self.innoSetup_installDir, "iscc.exe"), 
			*yieldSwitches(), 
			issFile or self.setupFile,
		]
		
		print(".iss Arguments:")
		for item in args:
			print(f"\t{item}")

		subprocess.call(args)

if (__name__ == "__main__"):
	directory = "H:/Python/Material_Tracker"

	exe = build_innoSetup()

	exe.name = "Material_Tracker"
	exe.publisher = "Decatur Mold"
	exe.icon = f"{directory}/resources/startIcon.ico"
	exe.publisherWebsite = "https://www.decaturmold.com/"

	exe.setDesktop(f"{directory}/runMe.py", workingDir = "\\\\dmte3\\MaterialDB", params = ("-cd",))
	exe.setStartMenu(f"{directory}/runMe.py", workingDir = "\\\\dmte3\\MaterialDB", params = ("-cd",))

	exe.create(outputDir = "\\\\dmte3\\MaterialDB\\Versions\\v3_1_0")
