import re,os
from ProgMenu.progmenu import MENU,EntryArg,EntryFlag,EntryPositional
# from progmenu import MENU,EntryArg,EntryFlag,EntryPositional

#-----------------------#
#    Entry Functions    #
#-----------------------#
def ignoreEntry(i):
	'''Takes a comma-separated list of status codes to ignore'''
	to_ret=[]

	for c in i.strip(',').split(','):
		try:
			to_ret.append(int(c))
		except ValueError:
			to_ret.append(c)

	return to_ret

def okcodesEntry(o):
	'''Takes a comma-separated list of status codes to accept'''
	try:
		return [int(i) for i in o.split(',')]
	except ValueError:
		print(f"[|x:ok_codes:error]: Invalid error codes! Ensure they're all ints!")

def timeoutEntry(t):
	'''Sets timeout per request'''
	try:
		to_ret=int(t)
		vprint(f"\033[93m[|x:timeout]:\033[0m Timeout -> 2 seconds")
	except ValueError:
		print(f"\033[91m[|x:timeout:error]:\033[0m Invalid int: {t}")
		exit(1)

def urlEntry(url):
	'''Uses regex to ensure the url is at least a valid format'''
	if not re.fullmatch("^http[s]?://.*",url):
		print(f"\033[91m[|x:url:error]:\033[0m This URL isn't valid: {url}")
		exit(1)
	return url

def helpEntry():
	'''Prints a help menu'''
	print('''webmap.py <url> [-acdghirt]
Finds links/resources on a web page
  <url>;                  The target url.
                          Note: This MUST be in format http(s)://url
  -a; --anchors;          Return anchors (#) that link to the current page.
                          Default is to ignore anchors
  -c; --ok_codes=<codes>; List of HTTP codes that are acceptable.
                          Comma separated.
                          The default list is all 2xx codes
  -d; --ignore-dir=<str>; Comma-separated list of directories to ignore.
                          Can be paths.
                          Useful to filter out common dirs like js, css, etc...
                          Use "DEFAULT" (case sensitive) to ignore common directories (listed below).
                          "DEFAULT" can be used with other custom dirs
  -g; --ignore=<codes>;   List of codes to ignore.
                          Comma separated.
                          See "Code List" below for a list of codes
  -h; --help;             Prints this page
  -i; --internal;         Only recurse into internal urls.
                          Internal urls are any that have the EXACT same domain (subdomains are counted as external)
  -r; --recurse;          Recursively search for links
  -t; --timeout;          Set timeout for requests, in seconds


    ___________
_-+* Code List *+-_
===================
  - FLAT;         Recursion is off
  - LOCK;         This url has already been seen, and won't be recursed into.
                  This prevents infinite loops
  - ERR;          There was an error trying to reach the url.
                  This can be a timeout, bad hostname, etc...
  - <HTTP Codes>; Any standard HTTP code (200,404,etc...)

    _____________
_-+* Ignore Dirs *+-_
=====================
  - List of common directories that are ignored by "DEFAULT" keyword:
  	js,images,css,fonts

    __________
_-+* Examples *+-_
==================
  - Scan https://example.com with recursion, but only recursing internal urls:
      ./webmap.py https://example.com --recurse --internal
  - Similar to above, but ignore "LOCK" and "ERR":
      ./webmap.py https://example.com -rig LOCK,ERR''')

def internalEntry():
	vprint(f"\033[93m[|x:internal]:\033[0m Don't recurse external URLs")
	return True

def recurseEntry():
	vprint(f"\033[93m[|x:recurse]:\033[0m Recursive check")
	return True

def ignoreDirsFunc(d):
	d=d.split(',')
	#Look for the "DEFAULT" keyword and substitute it with a list of common dirs
	if "DEFAULT" in d:
		d.remove("DEFAULT")
		d+=["js","images","css","fonts"]

	return d



#--------------------------#
#    Entry Declarations    #
#--------------------------#
EntryFlag("anchors",['a',"anchors"],lambda:True)
EntryArg("ok_codes",['c',"ok_codes"],okcodesEntry,default=[i for i in range(200,300)])
EntryArg("ignore_dirs",['d',"ignore-dirs"],ignoreDirsFunc)
EntryArg("ignore",['g',"ignore"],ignoreEntry,default=[])
EntryArg("timeout",['t',"timeout"],timeoutEntry,default=60)
EntryFlag("help",['h',"help"],helpEntry)
EntryFlag("internal",['i',"internal"],internalEntry)
EntryFlag("recurse",['r',"recurse"],recurseEntry)
EntryPositional("url",0,urlEntry,strict=False)


#-------------------------#
#    Utility Variables    #
#-------------------------#
vprint=MENU.verboseSetup(['v',"verbose"])
PARSER=MENU.parse(True,strict=True)
