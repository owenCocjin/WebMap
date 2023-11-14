import requests,re
import globe
from menu import vprint,PARSER

RED='\033[91m'
GREEN='\033[92m'
YELLOW='\033[93m'
BLUE='\033[94m'
CLR='\033[0m'

class Resource():
	'''This defines a single resource class'''
	seen_resources=[]  #List of full_urls that have already been seen (prevents infinite loops)
	ok_codes=PARSER["ok_codes"]

	def __init__(self,url:str, base:str='',name:str=None,_depth:int=0):
		'''Note: There's a priority to extract the base from the url vs taking the given base'''
		self.name=url if not name else name
		self.url=url
		if (new_base:=re.findall("^http[s]?:\/\/.*?[a-z0-9\.]+[:]?[0-9]{0,5}",url)):
			self.base=new_base[0]
		elif base:
			self.base=base 
		else:
			print(f"[|x:{self.url}]: No base found! This is a fatal error!")
			exit(3)
		# print(f"[|x:{self.url}]:self.base: {self.base}")
		self.domain=new_domain[0] if (new_domain:=re.findall("(?<=:\/\/)[a-z0-9\.\_\-]+[:]?[0-9]{0,5}",self.base)) else None
		self.full_url=url.strip('/') if re.fullmatch("^http[s]?:\/\/.*",self.url) else f"{self.base.strip('/')}/{self.url.strip('/')}"
		self.full_url=self.full_url.strip('#/?')  #Remove these characters from the end

		# if self.full_url in Resource.seen_resources:
		# 	print(f"[|x:{self.full_url}]: This URL has already been seen! Locking recurse!")
		# 	recurse=False
		# 	self.recurse_lock=True
		# else:
		# 	Resource.seen_resources.append(self.full_url)
		# 	self.recurse_lock=False
		self.recurse_lock=False

		self.status_code="FLAT"

		self.req=None
		self.links=[]  #List of Resource objects of links found in this page

		self._depth=_depth  #Just the number of spaces to print before this resource

		# print(f"[|x:{self.full_url}]: Resources seen: {Resource.seen_resources}")

	def __str__(self):
		to_ret=f"{('  '*self._depth)}[{BLUE}{self.url}{CLR} ({GREEN if self.status_code in Resource.ok_codes else RED}{self.status_code}{CLR})]: {RED if (links_count:=len(self.links))==0 else GREEN}{links_count}{CLR} links"
		for l in self.links:
			if l.status_code not in PARSER["ignore"]:
				to_ret+=f"\n{l}"

		return to_ret

	def __call__(self,recurse=False)->bool:
		'''Calling this object makes a call out to the url and saves the found resources within it'''
		templinks=[]
		self.links.clear()
		vprint(f"[|x:resources:Resources:__call__]: self.domain: {self.domain}")

		if self.full_url in Resource.seen_resources:
			vprint(f"[|x:{self.full_url}]: This URL has already been seen! Ignoring...")
			self.status_code="LOCK"
			return False
		elif PARSER["internal"] and not re.fullmatch(f"""^http[s]?:\/\/{self.domain}.*""",PARSER["url"]):
			vprint(f"[|x:{self.full_url}]: External! Ignoring...")
			self.status_code="EXT"
			return False
		else:
			Resource.seen_resources.append(self.full_url)

		vprint(f"[|x:{self.full_url}]: Getting page...")
		try:
			self.req=requests.get(self.full_url)
			self.status_code=self.req.status_code

			if self.status_code not in self.ok_codes:
				print(f"[|x:{self.full_url}]: Failed to get {self.full_url}: {self.status_code}")
				return False
		except Exception as e:
			regex_errmatch="\[Errno \-?[0-9]+.*(?=\')"
			print(f"[|x:{self.full_url}]: {e.__class__.__name__}: {err_msg[0] if (err_msg:=re.findall(regex_errmatch,str(e))) else e}")
			self.status_code="ERR"
			return False

		#Parse the returned data for links
		# templinks+=re.findall("""http[s]?:\/\/[a-zA-Z0-9\.\_\-]+:?[0-9]{0,5}(?=\/)?""",self.req.text)
		for r in globe.RE_SEARCHES:
			templinks+=re.findall(r,self.req.text)
			# print(f"[|x:resources:Resources:__call__]: templinks: {templinks}")			
		#De-duplicate links
		templinks=list(set(templinks))
		# print(f"[|x:{self.full_url}]: templinks: {templinks}")

		#Convert links to Resources
		for l in templinks:
			regex_results=re.fullmatch(f"""^http[s]?:[\/\/]?(?!.*\.{self.domain}).*""",l)
			# print(f"[|x:resources:Resources:__call__]: l: {l}")
			# print(f"[|x:resources:Resources:__call__]: regex: {regex_results}")
		  #Ignore links that are empty, anchored, external
			if not l or \
			(not PARSER["anchors"] and l[0]=='#') or \
			(PARSER["internal"] and regex_results) or \
			(PARSER["ignore_dirs"] and any([l.startswith(d) for d in PARSER["ignore_dirs"]])):
				vprint(f"[|x:resources:Resources:__call__]: Ignoring: {l}")
				continue
			self.links.append(Resource(l,base=self.base,_depth=self._depth+1))

		if not self.links:
			print(f"[|x:{self.full_url}]: No urls found!")
			return False

		if recurse and not self.recurse_lock:
			vprint(f"[|x:{self.full_url}]: Auto-recursing!")
			self.recurse(auto_recurse=True)
		elif self.recurse_lock:
			vprint(f"[|x:{self.full_url}]: Recurse locked!")

		return self.links

	def recurse(self,auto_recurse=False):
		'''Parse each link under this resource'''
		if self.recurse_lock:
			vprint(f"[|x:{self.full_url}]: Won't recurse (probably already seen)!")
			return False

		vprint(f"[|x:{self.full_url}]: Recursing through {len(self.links)} resources")
		for r in self.links:
			r(recurse=True)