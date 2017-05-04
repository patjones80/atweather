
'''
funcLib.py

Functions available to views.py for obtaining the weather forecast as a function of latitude/longitude

'''

import os, requests, collections

# define named tuple structure that will make up the locations dictionary
Location = collections.namedtuple('Location', 'Name Longitude Latitude State')

# these are the column numbers in the source file
(LOC_ID, LOC, LON, LAT, STATE) = (0, 1, 2, 3, 4)

# project's root directory
PARENT_DIR = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))

# define the National Weather Service URL for pulling forecasts

NWS_URL = 'https://api.weather.gov/points/%s,%s/forecast'
        
def getLocationList():

	LOCATIONS = dict()

	# use forward slashes in unix/linux
    
	if os.name == 'posix':
		f_locations = r'%s/at_shelter_list.txt' % PARENT_DIR
	else:
		f_locations = r'%s\at_shelter_list.txt' % PARENT_DIR

	# proceed with reading the location list in

	with open(f_locations, mode = 'r', encoding = 'UTF-8') as LocationFile:

		for line in LocationFile:
			line = list(line.strip('\n').split('\t'))
			cols = Location(Name = line[LOC], Longitude = line[LON], Latitude = line[LAT], State = line[STATE])

			LOCATIONS[int(line[LOC_ID])] = cols
	
	return LOCATIONS

#####

def getForecast(lat, lon):
    
    try:

        # NWS API formalism
        
        # TODO: insert proper header(s)
        # TODO: need to pass along proper SSL certification!
        
        response = requests.get(NWS_URL % (lat, lon), headers = { "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36" }, verify = False)
        forecast = response.json()
        
    except Exception as e:

        # check first for general exceptions
        return 'There was a error retrieving the forecast from the National Weather Service: %s' % repr(e)      

    
    # otherwise, we're good to go
    
    return forecast
    
