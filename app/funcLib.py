
'''
funcLib.py

Functions available to views.py for obtaining the weather forecast as a function of latitude/longitude

'''

import os
import requests

# these are the column numbers in the source file

(LOC_ID, LOC, LON, LAT, STATE) = (0, 1, 2, 3, 4)

# project's root directory

PARENT_DIR = os.path.join(os.path.dirname(__file__), '..')

# define the National Weather Service URL for pulling forecasts

# will be deprecated!
NWS_URL = 'http://forecast.weather.gov/MapClick.php?lon=%s&lat=%s&unit=0&lg=english&FcstType=text&TextType=1'

# TODO: change the development API endpoint to the production endpoint
# NWS_URL = 'https://api-v1.weather.gov/points/%s,%s/forecast'

#####

class Location():

    def __init__(self, curr_id):

        ForecastPoints = getLocationList()

        self.Name      = ForecastPoints[curr_id][LOC]
        self.Longitude = ForecastPoints[curr_id][LON]
        self.Latitude  = ForecastPoints[curr_id][LAT]
        self.State     = ForecastPoints[curr_id][STATE]

#####
        
def getLocationList():
    
    LOCATIONS = dict()

    with open('%s/at_shelter_list.txt' % PARENT_DIR, mode = 'r', encoding = 'UTF-8') as LocationFile:

        for line in LocationFile:

            line = line.strip('\n')
            
            cols = list(line.split('\t'))
            
            cols[0] = int(cols[0])
            
            LOCATIONS[int(cols[LOC_ID])] = cols            
            
    return LOCATIONS

#####

def AdjustHTML(html):

    # makes several formatting changes to the HTML returned from the NWS website
    
    formatted = html
    formatted = formatted.replace('<b>Last Update: </b></a>', '<b>Last Update</b></a>:')                                    # bring the colon outside the link text
    formatted = formatted.replace('margin-left:-40px;', '')                                                                 # dump the NWS's margin formatting
    formatted = formatted.replace('font-family: Arial !important', 'font-family: Trebuchet MS, Helvetica, sans-serif')      # modify the NWS's default font
    formatted = formatted.replace('<br>&nbsp;', ',')                                                                        # dump the line break

    # the links to hazardous weather warnings embedded in the NOAA page don't work unless replaced with the absolute URL

    formatted = formatted.replace('showsigwx.php', 'http://forecast.weather.gov/showsigwx.php')

    return formatted

#####

def getForecast(lat, lon):

    forecast_html = ''
    
    try:

        # for checking our logic
        # raise Exception('This is a bug, dude...', 123)

        # for production
        # forecast_html = requests.get(NWS_URL % (lon, lat), proxies = {'http':'http://proxy.server:3128'}).text

        # will be deprecated!
        
        forecast_html = requests.get(NWS_URL % (lon, lat)).text


        # NWS API formalism, now on hold until March 2017
        
        # TODO: insert proper header(s)
        # TODO: need to pass along proper SSL certification!
        # TODO: insert proxies argument for production?

##        print(NWS_URL % (lat, lon))
        
##        response = requests.get(NWS_URL % (lat, lon), headers = { "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36" }, verify = False)

##        print('The response is: ')
##        print(response)
##        
##        forecast = response.json()
        
    except Exception as e:

        # check first for general exceptions
        return 'There was a error retrieving the forecast from the National Weather Service: %s' % repr(e)      

    finally:

        # TODO: deprecate this error branch?
        
        if forecast_html.find('404 Not Found') >= 0:                                                            

            # then check if the HTML returned contained a 404 message

            return 'The National Weather Service returned a 404 error.'

        pass
    
    # otherwise, we're good to go
    
    return AdjustHTML(forecast_html)

##    return forecast
    
#####    

# testing

# curr_id = 0
# curr_id = int(input("Enter location ID: "))

# current_location = Location(curr_id = curr_id)

# print(getForecast(current_location.Latitude, current_location.Longitude))

