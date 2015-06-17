#!/usr/bin/python
import requests
import re
import sys
ar = {'-H' : '', '-P' : '888', '-u' : 'u', '-p': '3ware'}
#========== functions ==================================================================#
def GetFromWeb(useproxy=False): 
# {
	global ar
	base = "https://{}:{}/".format( ar['-H'], ar['-P'] )
	requests.packages.urllib3.disable_warnings()
	if useproxy == True:
		proxies = {"http": "http://au20320:as103200@138.21.89.90:3128/"}
	else:
		proxies = {}
	#uri = 'http://httpbin.org/post'
	uri = base + 'login.html'
	payload = {'whopwd': 'a',
				'thepwd': '3ware',
				'submit': 'Login'}
	s = requests.Session()
	try:
		r = s.post(uri, data=payload, proxies=proxies, verify=False)
	except :
		return -200, 'Error authorizing'
	rcookies = r.cookies
	#print len(rcookies)
	uri = base + 'index.html'
	#uri = "https://89.108.111.89:888/page0.html?c=0"
	try:
		r = s.get(uri, proxies=proxies, verify=False)
	except :
		return -201, 'Error getting hostname'
	
	m = re.findall("<title>.+? - (.+) - .+?</title>", r.content)
	if (len(m) > 0):
		serv = m[0]
	else:
		serv = ''
	#print serv
	
	uri = base + 'page0.html?c=0'
	try:
		r = s.get(uri, proxies=proxies, cookies=dict(TDMUSER=rcookies['TDMUSER']), verify=False)
	except :
		return -202, 'Error getting stats'
		
	if r.status_code == 200:
		return 0, serv, re.findall('td[^>]+?tableheader".*?(?:><.+?>|>)(.+?)<', r.content), re.findall('td[^>]+?tabledata".*?(?:><.+?>|>)(.+?)<', r.content)
	else:
		return -1, 'http error', r.status_code
# }
def GetArgs():
# {
	global ar
	if len(sys.argv) > 1 and len(sys.argv) != len(sys.argv)/2*2:
		for i in range(1, len(sys.argv)-1, 2):
			ar[sys.argv[i]] = sys.argv[i+1]
		return True
	elif len(sys.argv) == 1:
		pass #Man
	else:
		#print 'Inconsistent command line'
		return False
# }
GetArgs()
ret = GetFromWeb()
exitcode = 3
if (ret[0] == 0):
	if (ret[3][4] == "OK"):
		exitcode = 0
	else:
		exitcode = 2
	print "{} - {} ({} {} {}, {} {}, {} {})".format(ret[3][4], ret[1], ret[3][0], ret[2][1], ret[3][1], ret[2][2], ret[3][2], ret[2][3], ret[3][3])
else:
	print "UNKNOWN {}".format(ret[1:])
exit(exitcode)