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

# def GetForecast(lat, lon):

    # try:

		# # NWS API formalism

		# # TODO: insert proper header(s)
		# # TODO: need to pass along proper SSL certification!

def GetForecast(lat, lon):

	try:
		response = requests.get('https://api.weather.gov/points/{},{}/forecast'.format(lat, lon),
								headers = { "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36" },
								verify = True)

		forecast = response.json()
		
		if 'status' in forecast.keys() and forecast['status'] == 503:
			s = GetForecastByScraping(lat, lon)
		else:
			s = ''
			
			for d in forecast['properties']['periods']:
				s += '<p><b>{}</b>: {}</p>'.format(d['name'], d['detailedForecast'])

			if 'Columbus Day' in s:
				# this is to fix a problem with the site somehow caching old forecasts; eventually this has
				# to be fixed but for now here is the override
				
				s = GetForecastByScraping(lat, lon)

		s = s.replace('<b>', '<p><b>').replace('<br>\n<br>', '</p>')
		
		return {'forecast': s}
			
	except Exception as e:

		# check for general exceptions
		return {'error': '<p>There was an error retrieving the forecast for this location from the National Weather Service. Please try again later.</p>'.format(repr(e))}

def GetForecastByScraping(lat, lon):

	''' Pulls the forecast by scraping the HTML of the text-only NWS page; this is a fallback for
	    when the API is not functioning properly for a gridpoint'''
	
	forecast_html = requests.get('http://forecast.weather.gov/MapClick.php?lat={}&lon={}&unit=0&lg=english&FcstType=text&TextType=1'.format(lat, lon)).text
	s = ''
	
	for t in forecast_html.split('<b>')[3:]:
		s += '<b>' + t.split('<hr>')[0]
		# print('<b>' + t.split('<hr>')[0])
		
	return s

def GetZone(lat, lon, zoneType):

	''' NOAA uses identifiers for areas ("MOZ077", "ORZ011", etc) to issue watches and warnings to specific locales.
		This function can pull the zone assignment for a particular point given lat/lon, and with that we can then 
		obtain information from other API extensions that require the zone
		
		zoneType can be: 'forecastZone', 'fireWeatherZone', 'county'
		
		See for example: https://api.weather.gov/points/39.63,-77.56
	'''

	response = requests.get('https://api.weather.gov/points/{},{}'.format(lat, lon), headers = { "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36" }, verify = True)
	
	metadata = response.json()
	s = metadata['properties'][zoneType].split('/')
	zone = s[len(s)-1]

	return zone

def GetAlerts(lat, lon):

	''' Obtain any alerts for a given location. There are three types of zones for a given forecast point:
		forecast, fire weather and county. See for example: https://api.weather.gov/points/39.63,-77.56
	'''

	Alerts = []	# we will loop over this in the HTML template to display the alerts
	Params = ''

	for zType in [('forecastZone', 'warnzone'), ('fireWeatherZone', 'firewxzone'), ('county', 'warncounty')]:
	
		zoneCode = GetZone(lat, lon, zType[0])
		
		response = requests.get('https://api.weather.gov/alerts/active/zone/{}'.format(zoneCode),
								 headers = { "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36" },
								 verify  = True)

		try:
			alerts   = response.json()
			if zoneCode not in Params:

				# if the zone code is for the fire weather zone or county zone is the same as the 
				# forecast zone, then the hazard headline will duplicate; let's avoid that
				Alerts.append(alerts['features'][0]['properties']['headline'])

		except IndexError:
			pass
	
		Params   += '{}={}&'.format(zType[1], zoneCode)		# builds up the URL parameters that will redirect to the NWS warning page

	return (Alerts, Params)