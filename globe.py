seen_urls=[]  #List of seen URLs

#Regex searches to do on every page to find links
RE_SEARCHES=["""http[s]?:\/\/[a-zA-Z0-9\.\_\-\/\?\=]+:?[0-9]{0,5}[a-zA-Z0-9\.\_\-\/\?\=]+""",
						"""(?<=href=['"]).*?(?=['"\#])""",
						"""(?<=src=['"]).*?(?=['"\#])"""]