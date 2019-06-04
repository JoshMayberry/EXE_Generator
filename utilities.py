import os
import re
import shutil

import abc
import MyUtilities.common

data_files_zip = []
absPath = re.sub("([^\\\\])[\\\\]([^\\\\])", r"\1/\2", os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

class Utilities(MyUtilities.common.EnsureFunctions):
	pass

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

	def addFile(self, myInput, outputFolder = "", module = False, keepFolders = True, insideZip = False, ignore = None, zipOption = None):
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