#Version: 3.0.0

import re
import os
import sys
import shutil

import subprocess

import uuid
import stat
import site

from distutils.core import setup

from .utilities import Utilities

#Required Software
	#Inno Setup: http://www.jrsoftware.org/isdl.php

#Import User Modules
if (__name__ == "__main__"):
	sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))) #Allows to import from the parent directory

def build(*args, **kwargs):
	return Exe_InnoSetup(*args, **kwargs)

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
	def name(self, value, *, default = "MyApp"):
		"""What the program is called."""
		
		return value or default

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
	def pythonPath(self, value):
		"""Where pythonw.exe is installed at."""
		
		return self.ensure_filePath(value, ending = "python.exe", default = lambda: os.path.dirname(sys.executable))

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

		args = [
			os.path.join(self.innoSetup_installDir, "iscc.exe"), 
			*yieldSwitches(), 
			issFile or self.setupFile,
		]
		
		print(".iss Arguments:")
		for item in args:
			print(f"\t{item}")

		subprocess.call(args)

def copyFile(source, destination):
	os.makedirs(destination, exist_ok = True)
	
	if (not os.path.isdir(source)):
		print("@1", source, destination)
		shutil.copy2(source, destination)
		return

	print("@2", source, destination, os.path.basename(source))
	for item in os.listdir(source):
		if (item in ("__pycache__", ".git")):
			continue
		copyFile(os.path.join(source, item), os.path.join(destination, os.path.basename(source)))

# if (__name__ == "__main__"):
# 	directory = "H:/Python/Material_Tracker"
# 	sys.path.append(os.path.dirname(directory))

# 	import Material_Tracker.__version__
# 	version = f"v{Material_Tracker.__version__.major}_{Material_Tracker.__version__.minor}_{Material_Tracker.__version__.micro}{Material_Tracker.__version__.suffix}"
# 	versionPath = os.path.join("\\\\dmte3\\MaterialDB\\Versions", version)
# 	if (not os.path.exists(versionPath)):
# 		print("Copying version files...")
# 		os.makedirs(versionPath, exist_ok = True)

# 		source = "H:/Python/Material_Tracker/"
# 		for fileName in ("__version__.py", "_CHANGELOG.md", "controller.py", "runMe.py", "resources"):
# 			copyFile(os.path.join(source, fileName), versionPath)
# 		for fileName in ("Datalogic_USBCOMInstaller.msi",):
# 			copyFile(os.path.join(source, "docs", fileName), os.path.join(versionPath, "docs"))

# 		for fileName in ("__init__.py", "controller.py", "splash.py", "version.py", "LICENSE_forSections.py", "test_GUI_Maker.py"):
# 			copyFile(os.path.join("H:/Python/modules/GUI_Maker", fileName), os.path.join(versionPath, "GUI_Maker"))

# 		for fileName in ("__init__.py", "common.py", "debugging.py", "wxPython.py", "LICENSE_forSections.py"):
# 			copyFile(os.path.join("H:/Python/modules/Utilities", fileName), os.path.join(versionPath, "Utilities"))

# 		for fileName in ("__init__.py", "controller.py"):
# 			copyFile(os.path.join("H:/Python/modules/API_Com", fileName), os.path.join(versionPath, "API_Com"))

# 		for fileName in ("__init__.py", "controller.py"):
# 			copyFile(os.path.join("H:/Python/modules/API_Security", fileName), os.path.join(versionPath, "API_Security"))

# 		for fileName in ("__init__.py", "controller.py", "version.py"):
# 			copyFile(os.path.join("H:/Python/modules/API_Excel", fileName), os.path.join(versionPath, "API_Excel"))

# 		for fileName in ("__init__.py", "controller.py", "version.py"):
# 			copyFile(os.path.join("H:/Python/modules/API_Database", fileName), os.path.join(versionPath, "API_Database"))
# 		copyFile("H:/Python/modules/API_Database/alembic_templates", os.path.join(versionPath, "API_Database/alembic_templates"))

# 		copyFile("H:/Python/modules/forks/__init__.py", os.path.join(versionPath, "forks"))
# 		copyFile("H:/Python/modules/forks/objectlistview/__init__.py", os.path.join(versionPath, "forks/objectlistview"))
# 		copyFile("H:/Python/modules/forks/objectlistview/ObjectListView", os.path.join(versionPath, "forks/objectlistview"))
# 		copyFile("H:/Python/modules/forks/pypubsub/__init__.py", os.path.join(versionPath, "forks/pypubsub"))
# 		copyFile("H:/Python/modules/forks/pypubsub/src", os.path.join(versionPath, "forks/pypubsub"))
# 		copyFile("H:/Python/modules/forks/sqlalchemy", os.path.join(versionPath, "forks"))

# 	print("Creating Installer...")
# 	exe = build_innoSetup()

# 	exe.name = "Material_Tracker2"
# 	exe.publisher = "Decatur Mold"
# 	exe.icon = f"{directory}/resources/startIcon.ico"
# 	exe.publisherWebsite = "https://www.decaturmold.com/"

# 	exe.setDesktop(f"{directory}/runMe.py", workingDir = "\\\\dmte3\\MaterialDB", params = ("-cd",))
# 	exe.setStartMenu(f"{directory}/runMe.py", workingDir = "\\\\dmte3\\MaterialDB", params = ("-cd",))

# 	exe.create(outputDir = versionPath)
