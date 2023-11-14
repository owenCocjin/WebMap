import requests,re
import globe
from menu import PARSER,vprint

regex_errormatch="\[Errno [0-9]+.*(?=\')"

def req_check(func):
	'''Checks if the request was successful'''
	def wrapper(*args,**kwargs):
		try:
			req=func(*args,timeout=PARSER["timeout"],**kwargs)
		except requests.exceptions.ConnectionError as e:
			print(f"""\033[91m[|x:{PARSER["url"]}:{e.__class__.__name__}]:\033[0m {re.findall(regex_errormatch,str(e))[0]}""")
			raise e

		if not 200<=req.status_code<=299:
			vprint(f"""[|x:{PARSER["url"]}]: Failed with {req.status_code}!""")
		return req
	return wrapper


@req_check
def get(*args,**kwargs):
	return requests.get(*args,**kwargs)


def getPageURLs(url):
	to_ret=[]

	req=get(url)
	if type(req)!=requests.models.Response:
		return None,None

	#Parse the file for resources.
	#Because some links might be relative, we'll need to check the actual "href" and "src"
	to_ret+=re.findall("""http[s]?:\/\/[a-zA-Z0-9\.\/]+""",req.text)
	to_ret+=re.findall("""(?<=href=['"]).*?(?=['"])""",req.text)
	to_ret+=re.findall("""(?<=src=['"]).*?(?=['"])""",req.text)
	to_ret+=re.findall(""" """,req.text)

	#De-duplicate
	to_ret=list(set(to_ret))

	return to_ret

def searchURLs(urls,base=''):
	'''Get all URLs in the list of given urls'''
	to_ret={}

	for u in urls:
		print(f"[|x:searchURLs]: Trying {u}...")
		orig_url=u

		#Format the url so it's is proper http format
		if not re.fullmatch("^http[s]?://.*",u):
			vprint(f"[|x:searchURLs:add base]: {u} -> ",end='')
			u=f"{base.strip('/')}/{u.strip('/')}"
			vprint(u)

		if u in globe.seen_urls:
			vprint(f"[|x:searchURLs]: Already seen {u}!")
			continue
		globe.seen_urls.append(u)

		if PARSER["internal"] and not u.startswith(base):
			vprint(f"\033[93m[|x:searchURLs:external]:\033[0m Skipping: {u}...")
			continue

		found_urls=getPageURLs(u)
		if not found_urls:
			print(f"[|x:{u}]: No URLs found!")
			continue

		# if PARSER["recurse"]:
		# 	sub_urls=searchURLs(found_urls,base)
		# 	all_sub_urls=[]
		# 	for i in sub_urls.values():
		# 		all_sub_urls+=i

		# 	for s in all_sub_urls:
		# 		to_ret[orig_url]
		# else:
		# 	to_ret[orig_url]=found_urls
		to_ret[u]=found_urls



	return to_ret