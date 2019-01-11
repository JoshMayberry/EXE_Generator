#Version: 3.0.0

import os
import sys

import py2exe
from distutils.core import setup

from .utilities import absPath
from .utilities import Exe_Base
from .utilities import data_files_zip

#Required Modules
##py -m pip install
	# py2exe

#Import User Modules
if (__name__ == "__main__"):
	sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))) #Allows to import from the parent directory

#Controllers
def build(*args, **kwargs):
	return Exe_Py2Exe(*args, **kwargs)

class Exe_Py2Exe(Exe_Base):
	def __init__(self, *args, **kwargs):
		"""Used to create a .exe file.
		For good module structure practices, see: http://blog.habnab.it/blog/2013/07/21/python-packages-and-you/
		Special thanks to Ned Deily for how to detect 32 bit vs 64 bit on https://stackoverflow.com/questions/6107905/which-command-to-use-for-checking-whether-python-is-64bit-or-32bit/12057504#12057504

		mainFile (str) - The name of the main .py file

		Example Input: Exe_Py2Exe("runMe")
		"""

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
