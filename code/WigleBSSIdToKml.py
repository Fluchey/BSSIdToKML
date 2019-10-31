import os, sys, argparse, requests, json, simplekml
from requests.auth import HTTPBasicAuth

def loadConfigFile():
	global APINAME
	global APITOKEN
	try:
		with open(os.path.join(sys.path[0], "config.txt"), "r") as confFile:
			lines = confFile.readlines()
			APINAME = lines[0].strip()
			APITOKEN = lines[1].strip()	
	except FileNotFoundError:
		print("The config file was not found. Make sure config.txt exists in the same folder as the script.")
		print("Exiting program..")
		sys.exit()

def loadBSSIdFile(input):
	BSSIdList = []
	try:	
		with open(input) as file:
			for line in file:
				BSSIdList.append(line.rstrip())
	except:
		print("Error loading BSSId file..")
		print("Exiting program")
		sys.exit()
	return BSSIdList

def wigleRequest(BSSId):
	global KML
	try:
		print("Sending request to wigle for BSSId: ", BSSId)
		r = requests.get('https://api.wigle.net/api/v2/network/detail?netid=' + BSSId, auth=HTTPBasicAuth(APINAME, APITOKEN))
		j = r.json()

		#with open("/Users/anton/Documents/Programming/WigleBSSIdToKml/code/jsonTrue.json") as jsonFile:
		#	j = json.load(jsonFile)
		
		if j['success'] == False:
			print(BSSId, j['message'])
		elif j['success'] == True:
			ssid = j['results'][0]['locationData'][0]['ssid']
			latitude = j['results'][0]['locationData'][0]['latitude']
			longitude = j['results'][0]['locationData'][0]['longitude']
			KML.newpoint(name=ssid, coords=[(longitude, latitude)])
			print(ssid, "added to KML \n\tBSSId:\t" + BSSId, "\n\tlat:\t" + str(latitude), "\n\tlon:\t" + str(longitude))
	except Exception as e:
		print(e)


# PARSE ARGUMENTS
parser = argparse.ArgumentParser(description='Convert a list of BSSId:s to a kml-file using the wigle.net API. Input a list of BSSId:s, one entry per line. Requires a file "config.txt" in the same folder as the script with your API NAME on the top line and API TOKEN on the bottom line')
parser.add_argument('input', help='The BSSId list to be processed')
parser.add_argument('-o', '--output', help="Output filename without extension. If no output is specified the output filename will be the same as input")
args = parser.parse_args()

# INITIALIZE EMPTY VARIABLES
APINAME = ""
APITOKEN = ""
KML = simplekml.Kml()

# LOAD BSSIDLIST
BSSIdList = loadBSSIdFile(args.input)

# LOAD CONFIGURATION
loadConfigFile()

# LOOP OVER ALL BSSID:S IN LIST
for line in BSSIdList:
	wigleRequest(line.rstrip())

# SAVE FINAL KML. IF OUTPUT IS NOT SET, SET NAME TO SAME AS INPUT
if not args.output:
	args.output = os.path.splitext(args.input)[0]
KML.save(args.output + ".kml")

print("\nSCRIPT FINISHED")
print("KML file saved as " + args.output + ".kml")
