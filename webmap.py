#!/usr/bin/python3
import requests,re,json
import resources
from menu import PARSER,vprint

def main():
	# vprint(MENU)
	# vprint(PARSER)

	#First thing is to get the contents of the first website.
	#I just realized we can leverage the return headers to see if it's HTML or json, etc... that's returned
	print(f"""[|x:main]: Fetching base URL @ {PARSER["url"]}...""")

	homepage=resources.Resource(PARSER["url"])
	homepage(PARSER["recurse"])
	print(f"\n{homepage}")











if __name__=="__main__":
	try:
		main()
	except KeyboardInterrupt:
		print("\r\033[K", end="")
