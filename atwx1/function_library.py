'''
function_library.py
Functions available to views.py for obtaining the weather forecast as a function of latitude/longitude

Three different API calls are used:

(1) pull alerts based on forecast zone - 	https://api.weather.gov/alerts/active/zone/{}
(2) get metadata about a lat/lon point -	https://api.weather.gov/points/{},{}
(3) get the forecast for lat/lon point -	https://api.weather.gov/points/{},{}/forecast

'''

import collections
import os
import requests

# define named tuple structure that will make up the locations dictionary
location = collections.namedtuple('location', 'name longitude latitude state trail')

# these are the column numbers in the source file
(LOC_ID, LOC, LON, LAT, STATE, TRAIL) = (0, 1, 2, 3, 4, 5)

# project's root directory
CURR_DIR = os.path.dirname(os.path.abspath( __file__ ))
        
def get_location_list():
	locations = dict()

	# use forward slashes in unix/linux
	if os.name == 'posix':
		f_locations = r'{}/at_shelter_list.txt'.format(CURR_DIR)
	else:
		f_locations = r'{}\at_shelter_list.txt'.format(CURR_DIR)

	# proceed with reading the location list in
	with open(f_locations, mode = 'r', encoding = 'UTF-8') as location_file:
		for line in location_file:
			line = list(line.strip('\n').split('\t'))
			cols = location(name = line[LOC], longitude = line[LON], latitude = line[LAT], state = line[STATE], trail = line[TRAIL])

			locations[int(line[LOC_ID])] = cols
	
	return locations

#####

# def GetForecast(lat, lon):
    # try:
		# # NWS API formalism

		# # TODO: insert proper header(s)
		# # TODO: need to pass along proper SSL certification!

def get_forecast(lat, lon):

	try:
		response = requests.get('https://api.weather.gov/points/{},{}/forecast'.format(lat, lon),
								headers={ "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36" },
								verify=True)

		forecast = response.json()
		
		if 'status' in forecast.keys() and forecast['status'] == 503:
			s = get_forecast_by_scraping(lat, lon)
		else:
			s = ''

			for d in forecast['properties']['periods']:
				s += '<p><b>{}</b>: {}</p>'.format(d['name'], d['detailedForecast'])

			if 'Columbus Day' in s:
				# this is to fix a problem with the site somehow caching old forecasts; eventually this has
				# to be fixed but for now here is the override
				s = get_forecast_by_scraping(lat, lon)

		s = s.replace('<b>', '<p><b>').replace('<br>\n<br>', '</p>')
		
		return {'forecast': s}
			
	except Exception as e:
		# check for general exceptions
		return {'error': 'There is no forecast available right now for the location you selected.'}

def get_forecast_by_scraping(lat, lon):

	''' Pulls the forecast by scraping the HTML of the text-only NWS page; this is a fallback for
	    when the API is not functioning properly for a gridpoint'''
	
	forecast_html = requests.get('http://forecast.weather.gov/MapClick.php?lat={}&lon={}&unit=0&lg=english&FcstType=text&TextType=1'.format(lat, lon)).text
	s = ''
	
	for t in forecast_html.split('<b>')[3:]:
		s += '<b>' + t.split('<hr>')[0]
		
	s = s.replace('<b>', '<p><b>').replace('<br>\n<br>', '</p>')
	
	return s

def get_zone(lat, lon, zone_type):

	''' NOAA uses identifiers for areas ("MOZ077", "ORZ011", etc) to issue watches and warnings to specific locales.
		This function can pull the zone assignment for a particular point given lat/lon, and with that we can then 
		obtain information from other API extensions that require the zone
		
		zoneType can be: 'forecastZone', 'fireWeatherZone', 'county'
		
		See for example: https://api.weather.gov/points/39.63,-77.56
	'''

	response = requests.get('https://api.weather.gov/points/{},{}'.format(lat, lon), headers = { "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36" }, verify = True)
	
	metadata = response.json()
	s = metadata['properties'][zone_type].split('/')
	zone = s[len(s)-1]

	return zone

def get_alerts(lat, lon):

	''' Obtain any alerts for a given location. There are three types of zones for a given forecast point:
		forecast, fire weather and county. See for example: https://api.weather.gov/points/39.63,-77.56
	'''

	all_alerts = []	# we will loop over this in the HTML template to display the alerts

	forecast_zone = get_zone(lat, lon, 'forecastZone')
	fire_zone     = get_zone(lat, lon, 'fireWeatherZone')
	county_zone   = get_zone(lat, lon, 'county')
	
	response = requests.get('https://api.weather.gov/alerts/active/zone/{}'.format(county_zone),
							 headers={ "User-Agent": "https://www.atweather.org; Python 3.6/Django 1.11" },
							 verify=True)

	try:
		results = response.json()
		for alerts in results['features']:
			p = alerts['properties']
			if ("https://api.weather.gov/zones/forecast/" + forecast_zone in p['affectedZones'] or 
			    "https://api.weather.gov/zones/fire/"     + fire_zone     in p['affectedZones'] or 
			    "https://api.weather.gov/zones/county/"   + county_zone   in p['affectedZones']):
			   
				alert = collections.namedtuple('alert', 'warnzone warncounty headline event')
				all_alerts.append(alert(warnzone = forecast_zone, warncounty = county_zone, headline = p['headline'], event = p['event'].replace(' ', '+')))

	except IndexError:
		pass

	return all_alerts