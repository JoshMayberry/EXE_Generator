#Version: 3.0.0

import os
import sys
import shutil

import re
import abc
import inspect

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

class Exe_Base(object, metaclass = abc.ABCMeta):
	def __init__(self, mainFile):
		"""Used to create a .exe file.
		For good module structure practices, see: http://blog.habnab.it/blog/2013/07/21/python-packages-and-you/
		Special thanks to Ned Deily for how to detect 32 bit vs 64 bit on https://stackoverflow.com/questions/6107905/which-command-to-use-for-checking-whether-python-is-64bit-or-32bit/12057504#12057504

		mainFile (str) - The name of the main .py file

		Example Input: Exe("runMe")
		"""
		
		self.options = {}
		self.options["optimize"] = 0
		self.options["excludes"] = []
		self.options["includes"] = []

		self.console = {}
		self.console["script"] = ""

		self.name = ''
		self.version = ''
		self.description = ''
		self.author = ''
		self.data_files = []

		self.noError = True
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

	@abc.abstractmethod
	def setName(self, *args, **kwargs):
		pass

	def setMain(self, fileName):
		"""Sets the file path to the main .py file.

		fileName (str) - The name for the main .py file

		Example Input: setMain("convertToExcel")
		"""

		if (os.path.exists(fileName + ".py")):
			self.console["script"] = fileName + ".py"
		else:
			print("File does not exist.")
			self.noError = False

	@abc.abstractmethod
	def setIcon(self, *args, **kwargs):
		pass

	def setInfoName(self, name):
		"""Sets the name for the .exe file's info

		name (str) - The version number. Can be an int, float, or double.

		Example Input: setInfoName("start")
		"""

		self.name = name

	def setInfoVersion(self, version):
		"""Sets the version number for the .exe file's info

		version (str) - The version number. Can be an int, float, or double.

		Example Input: setInfoVersion("1.0")
		"""

		#Ensure correct data type
		if (type(version) != str):
			version = str(version)

		self.version = version

	def setInfoDescription(self, description):
		"""Sets the icon for the .exe file's info

		description (str) - What the program is meant to do

		Example Input: setInfoDescription("Converts a .ias file to an excel sheet")
		"""

		self.description = description

	def setInfoAuthor(self, author):
		"""Sets the author for the .exe file's info

		author (str) - Who created the program

		Example Input: setInfoAuthor("Joshua Mayberry")
		"""

		self.author = author

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

		Example Input: Exe("runMe")
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

	def setMain(self, fileName):
		"""Sets the file path to the main .py file.

		fileName (str) - The name for the main .py file

		Example Input: setMain("convertToExcel")
		"""

		if (os.path.exists(fileName + ".py")):
			self.console["script"] = fileName + ".py"
		else:
			print("File does not exist.")
			self.noError = False

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

		if (not self.noError):
			print ("An error has occured\n.exe creation abotred")
			
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

		Example Input: Exe("runMe")
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

		if (not self.noError):
			print ("An error has occured\n.exe creation abotred")
			return

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

		Example Input: Exe("runMe")
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

	def optimizeSize(self, excludeInterpreter = False, safer = False):
		"""Makes the overall program smaller.

		excludeInterpreter (bool) - If True: The Python interpreter will not be bundled
		safer (bool) - There are some things that some computers don't have. Enable this to include those redundancies

		Example Input: optimizeSize()
		"""

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

		if (not self.noError):
			print ("An error has occured\n.exe creation abotred")
			return

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

	def _example(self):
		"""Example Use:
			exe = Exe_Pynsist("runMe")
			exe._example()
		"""

		#Add settings
		self.optimizeSize()
		
		import __version__
		self.setName("start")
		self.setDestination(f"C:/Users/jmayberry/Desktop/materialTrackerProgram_{__version__.version}")
		self.setIcon("resources/startIcon")
		self.setInfoName(f"materialTracker")
		self.setInfoVersion(__version__.version)
		self.setInfoDescription("Manages Inventory")
		self.setInfoAuthor("Joshua Mayberry")

		#Add program files
		self.addInclude(["GUI_Maker", "API_Database", "API_Excel", "API_Com", "Utilities"])
		self.addFile("controller.py", "pkgs")
		self.addFile("../modules/forks", "pkgs")
		self.addFile("__version__.py", "pkgs")

		self.addFile("resources", "")
		self.addFile("_CHANGELOG.md", "")
		self.addFile("__version__.py", "")
		# self.addExclude(["pubsub"])

		#Add required installers
		self.addInstaller("docs/Datalogic_USBCOMInstaller.msi", message = "", installType = 0, condition = {"not_inRegistry": ("HKLM", "DRIVERS\DriverDatabase\DriverInfFiles\oem187.inf", "Active", "")})

		#Setup docs
		self.addFile("docs", "")
		self.addFile("runMe.py", "docs/code")
		self.addFile("setup.py", "docs/code")
		self.addFile("__init__.py", "docs/code")
		self.addFile("_CHANGELOG.md", "docs/code")
		self.addFile("controller.py", "docs/code")
		self.addFile("__version__.py", "docs/code")
		self.addFile("test_Material_Tracker.py", "docs/code")

		self.addFile("../modules/API_COM/controller.py", "docs/code/modules/API_COM", buildName = "API_COM_controller.py")
		self.addFile("../modules/API_Database/controller.py", "docs/code/modules/API_Database", buildName = "API_Database_controller.py")
		
		self.addFile("../modules/GUI_Maker/controller.py", "docs/code/modules/GUI_Maker", buildName = "GUI_Maker_controller.py")
		self.addFile("../modules/GUI_Maker/Splash.py", "docs/code/modules/GUI_Maker", buildName = "GUI_Maker_Splash.py")
		self.addFile("../modules/GUI_Maker/test_GUI_Maker.py", "docs/code/modules/GUI_Maker", buildName = "GUI_Maker_test_GUI_Maker.py")
		self.addFile("../modules/GUI_Maker/docs", "docs/code/modules/GUI_Maker")
		self.addFile("../modules/GUI_Maker/examples", "docs/code/modules/GUI_Maker")

		#Finalize .self
		self.create(include_cmd = True)
		# self.create()

if __name__ == '__main__':
	exe = Exe_Pynsist("runMe")
	exe._example()