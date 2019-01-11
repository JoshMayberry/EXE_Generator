#Version: 3.0.0

import os
import sys

import site
import glob
import modulefinder

# import nsist
import forks.pynsist.nsist as nsist #Use my own fork

from distutils.core import setup

from .utilities import absPath
from .utilities import Exe_Base

#Required Modules
##py -m pip install
	# nsist
	# win_cli_launchers

#Import User Modules
if (__name__ == "__main__"):
	sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))) #Allows to import from the parent directory

#Controllers
def build(*args, **kwargs):
	return Exe_Pynsist(*args, **kwargs)

class Exe_Pynsist(Exe_Base):
	def __init__(self, mainFile):
		"""Used to create a .exe file.
		For good module structure practices, see: http://blog.habnab.it/blog/2013/07/21/python-packages-and-you/
		Special thanks to Ned Deily for how to detect 32 bit vs 64 bit on https://stackoverflow.com/questions/6107905/which-command-to-use-for-checking-whether-python-is-64bit-or-32bit/12057504#12057504

		mainFile (str) - The name of the main .py file

		Example Input: Exe_Pynsist("runMe")
		"""

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

