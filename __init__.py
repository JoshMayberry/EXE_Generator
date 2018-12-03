import lazyLoad
lazyLoad.load(
	"uuid",
	"stat", 
	"site", 
	"glob", 
	"zipfile", 
	"modulefinder", 

	"py2exe", 
	"cx_Freeze", 
	"distutils", 
	# "pynsist", 
	"forks.pynsist.nsist", 
)

#Import the controller module as this namespace
from .controller import *
del controller