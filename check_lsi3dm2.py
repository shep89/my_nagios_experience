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
	payload = {'whopwd': ar['-u'],
				'thepwd': ar['-p'],
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
	stats = r.content
	
	uri = base + 'page1_1.html?c=0&u=-2'
	try:
		r = s.get(uri, proxies=proxies, cookies=dict(TDMUSER=rcookies['TDMUSER']), verify=False)
	except :
		return -202, 'Error getting volumes'
	volumes = r.content
	
	uri = base + 'page1_2.html?c=0'
	try:
		r = s.get(uri, proxies=proxies, cookies=dict(TDMUSER=rcookies['TDMUSER']), verify=False)
	except :
		return -202, 'Error getting volumes'
	disks = r.content
	
	if r.status_code == 200:
		return 0, serv, stats, volumes, disks
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
if (ret[0] == 0):
	prep = re.findall('td[^>]+?tabledata.*?(?:><.+?>|>)(.*?)<', ret[2])
	stat = []
	for i in range(0,len(prep), 6):
		stat.append(prep[i:i+6])
		#print prep[i:i+6]
	#print stat
	#print "==="

	vol = []
	prep = re.findall('td[^>]+?tabledata.*?(?:><.+?>|>)(.*?)<', ret[3])
	for i in range(0,len(prep), 6):
		vol.append(prep[i:i+5])
		#print prep[i:i+5]
	#print vol
	#print "==="

	disk = []
	prep = re.findall('td[^>]+?tabledata.*?(?:><.+?>|>)(.*?)<', ret[4])
	for i in range(0,len(prep), 9):
		disk.append(prep[i:i+8])
		#print prep[i:i+8]
	#print disk

	exitcode = 3


	statret = 3
	statout = ''
	statperf = ''
	ok = 0
	for n in stat:
		if (n[-1] == "OK" ):
			ok += 1
			if (statret == 3):
				statret = 0
		else:
			statret = 2
			statout += " " + n[1] + "("+ n[2] + ")"
	if (statret == 0):
		statout = "Controllers: OK"
	statperf = 'ControllersNotOk=' + str(len(stat)-ok)
	#print statout


	volret = 3
	volout = ''
	volperf = ''
	ok = 0
	for n in vol:
		if (n[-1] == "OK" ):
			ok += 1
			if (volret == 3):
				volret = 0
		else:
			volret = 2
			volout += " vol[{}] ({})".format(n[0], ', '.join(n[1:]))	

	if (volret == 0):
		volout = "Volumes: OK"
	volperf = 'VolumesNotOk=' + str(len(vol)-ok)
	#print volout


	diskret = 3
	diskout = ''
	diskperf = ''
	ok = 0
	for n in disk:
		if (n[-1] == "OK" ):
			ok += 1
			if (diskret == 3):
				diskret = 0
		else:
			diskret = 2
			diskout += " disk[{}] ({})".format(n[0], n[1], n[-1])
		

	if (diskret == 0):
		diskout = "Disks: OK"
	diskperf = 'DisksNotOk=' + str(len(disk)-ok)
	#print diskout

	if (statret == 2 or volret == 2 or diskret == 2):
		exitcode = 2
	elif (statret == 0 and volret == 0 and diskret == 0):
		exitcode = 0

	print "{} {}; {}; {}|{} {} {}".format(re.sub('\\..+', '', ret[1]), statout, volout, diskout, statperf, volperf, diskperf)

else:
	print "UNKNOWN {}".format(ret[1:])
exit(exitcode)
