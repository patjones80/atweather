'''
funcLib.py
Functions available to views.py for obtaining the weather forecast as a function of latitude/longitude

Three different API calls are used:

(1) pull alerts based on forecast zone - 	https://api.weather.gov/alerts/active/zone/{}
(2) get metadata about a lat/lon point -	https://api.weather.gov/points/{},{}
(3) get the forecast for lat/lon point -	https://api.weather.gov/points/{},{}/forecast

'''

import os, collections, requests

# define named tuple structure that will make up the locations dictionary
Location = collections.namedtuple('Location', 'Name Longitude Latitude State Trail')

# these are the column numbers in the source file
(LOC_ID, LOC, LON, LAT, STATE, TRAIL) = (0, 1, 2, 3, 4, 5)

# project's root directory
CURR_DIR = os.path.dirname(os.path.abspath( __file__ ))
        
def getLocationList():

	LOCATIONS = dict()

	# use forward slashes in unix/linux
    
	if os.name == 'posix':
		f_locations = r'{}/at_shelter_list.txt'.format(CURR_DIR)
	else:
		f_locations = r'{}\at_shelter_list.txt'.format(CURR_DIR)

	# proceed with reading the location list in

	with open(f_locations, mode = 'r', encoding = 'UTF-8') as LocationFile:

		for line in LocationFile:
			line = list(line.strip('\n').split('\t'))
			cols = Location(Name = line[LOC], Longitude = line[LON], Latitude = line[LAT], State = line[STATE], Trail = line[TRAIL])

			LOCATIONS[int(line[LOC_ID])] = cols
	
	return LOCATIONS

#####

def GetForecast(lat, lon):
    
    try:

        # NWS API formalism
        
        # TODO: insert proper header(s)
        # TODO: need to pass along proper SSL certification!
        
        response = requests.get('https://api.weather.gov/points/{},{}/forecast'.format.(lat, lon), headers = { "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36" }, verify = True)
        forecast = response.json()
        
    except Exception as e:

        # check first for general exceptions
        return 'There was a error retrieving the forecast from the National Weather Service: {}'.format(repr(e))

    # otherwise, we're good to go
    
    return forecast
	
def GetZone(lat, lon, zoneType):

	''' NOAA uses identifiers for areas ("MOZ077", "ORZ011", etc) to issue watches and warnings to specific locales.
		This function can pull the zone assignment for a particular point given lat/lon, and with that we can then 
		obtain information from other API extensions that require the zone
		
		zoneType can be: 'forecastZone', 'fireWeatherZone', 'county'
	'''
	
	response = requests.get('https://api.weather.gov/points/{},{}'.format(lat, lon), headers = { "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36" }, verify = True)

	metadata = response.json()
	zone = metadata['properties'][zoneType].split('/')[5]

	return zone

def GetAlerts(lat, lon):

	''' Obtain any alerts for a given location 
	'''

	Alerts = []

	for zType in ['forecastZone', 'fireWeatherZone', 'county']:
	
		response = requests.get('https://api.weather.gov/alerts/active/zone/{}'.format(GetZone(lat, lon, zType)),
								 headers = { "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36" },
								 verify  = True)

		alerts   = response.json()

		try:
			Alerts.append(alerts['features'][0]['properties']['headline'])
			
		except IndexError:
			pass
	
	return Alerts