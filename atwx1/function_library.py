'''
function_library.py
Functions available to views.py for obtaining the weather forecast as a function of latitude/longitude

Three different API calls are used:

(1) pull alerts based on forecast zone -    https://api.weather.gov/alerts/active/zone/{}
(2) get metadata about a lat/lon point -    https://api.weather.gov/points/{},{}

The metadata endpoint above contains the forecast endpoint under "properties" --> "forecast". This is
the URL that should be called in order to obtain the forecast text for the location in question.

'''

import collections
import json
import os
import requests
import time

# The headers dict that we'll use in our api calls
HEADERS = { "User-Agent": "https://www.atweather.org; Python 3.10.5/Django 4.1.4" }

# Define named tuple structure that will make up the locations dictionary
location = collections.namedtuple('location', 'seq name longitude latitude state trail')

# These are the column numbers in the source file
(LOC_ID, LOC, LON, LAT, STATE, TRAIL) = (1, 2, 3, 4, 5, 6)

# Project's root directory
CURR_DIR = os.path.dirname(os.path.abspath( __file__ ))

def call_url(url, headers=HEADERS, verify=True, attempt=1):
    # We use this logic repeatedly so let's make it a function
    r = requests.get(url, headers=headers, timeout=30, verify=verify)
    status_code = r.status_code

    if status_code == 200:
        try:
            return r.json()

        except json.decoder.JSONDecodeError:
            # If the fall back HTML scraper is the caller, we need
            # to return text, not a dict
            return r.text
    else:
        # Let's try twice more
        attempt += 1

        if attempt > 3:
            raise Exception(f'{url} returned status code {status_code}')

        time.sleep(attempt)
        return call_url(url, attempt=attempt)

def get_location_list():
    locations = collections.OrderedDict()
    seq = 0
    f_locations = f'{CURR_DIR}\\at_shelter_list.txt'

    # Use forward slashes in unix/linux
    if os.name == 'posix':
        f_locations = f'{CURR_DIR}/at_shelter_list.txt'

    # Proceed with reading the location list in
    with open(f_locations, mode='r', encoding='UTF-8') as location_file:
        for line in location_file:
            line = list(line.strip('\n').split('\t'))
            cols = location(seq, name=line[LOC], longitude=line[LON], latitude=line[LAT], state=line[STATE], trail=line[TRAIL])

            locations[line[LOC_ID]] = cols
            seq += 1

    return locations

def move(locations, id, dir=1):
    ''' Get previous or next entry given current location id 
        and value of the dir argument
        
        Arguments:
            - locations: dict containing all locations
            - id: id of the current location
            - dir: 1 = get next location, -1 = get previous location
    '''
    l = list(locations.keys())
    
    seq = locations[id].seq
    seq += dir
    
    try:
        result = l[seq]
    except IndexError:
        if seq != -1:
            result = l[0]
    
    return result

def get_forecast(lat, lon):
    ''' Call the NWS REST API
        # TODO: need to pass along proper SSL certification!
    '''
    try:
        r = call_url(f'https://api.weather.gov/points/{lat},{lon}')

        # Obtain the URL for the forecast endpoint
        forecast_url = r['properties']['forecast']
        print(forecast_url)

        # Now call the forecast endpoint
        r = call_url(forecast_url)

        s = ''
        for d in r['properties']['periods']:
            s += f"<p><b>{d['name']}</b>: {d['detailedForecast']}</p>"

        s = s.replace('<b>', '<p><b>').replace('<br>\n<br>', '</p>')

        #if not s:
        #    raise Exception('Empty forecast string')

        return s

    except Exception as e:
        # In the event that there's a problem fall back to HTML scraping
        print(f'Problem with getting API based forecast: {e}')
        return get_forecast_by_scraping(lat, lon)

def get_forecast_by_scraping(lat, lon):
    ''' Pulls the forecast by scraping the HTML of the text-only NWS page; this is a fallback for
        when the API is not functioning properly for a gridpoint
    '''
    url = f'http://forecast.weather.gov/MapClick.php?lat={lat}&lon={lon}&unit=0&lg=english&FcstType=text&TextType=1'
    forecast_html = call_url(url)
    s = ''

    for t in forecast_html.split('<b>')[3:]:
        s += f"<b>{t.split('<hr>')[0]}"

    s = s.replace('<b>', '<p><b>').replace('<br>\n<br>', '</p>')

    if not s:
        raise Exception(f'Empty forecast string or bad request in get_forecast_by_scraping: {url}')

    return s

def get_zone(lat, lon, zone_type):
    ''' NOAA uses identifiers for areas ("MOZ077", "ORZ011", etc) to issue watches and warnings to specific locales.
        This function can pull the zone assignment for a particular point given lat/lon, and with that we can then
        obtain information from other API extensions that require the zone

        zoneType can be: 'forecastZone', 'fireWeatherZone', 'county'

        See for example: https://api.weather.gov/points/39.63,-77.56
    '''
    r = call_url(f'https://api.weather.gov/points/{lat},{lon}')

    s = r['properties'][zone_type].split('/')
    zone = s[len(s)-1]

    return zone

def get_alerts(lat, lon):
    ''' Obtain any alerts for a given location. There are three types of zones for a given forecast point:
        forecast, fire weather and county. See for example: https://api.weather.gov/points/39.63,-77.56
    '''
    all_alerts = []  # we will loop over this in the HTML template to display the alerts

    forecast_zone = get_zone(lat, lon, 'forecastZone')
    fire_zone     = get_zone(lat, lon, 'fireWeatherZone')
    county_zone   = get_zone(lat, lon, 'county')

    r = call_url(f'https://api.weather.gov/alerts/active/zone/{county_zone}')

    try:
        for alerts in r['features']:
            p = alerts['properties']
            if ("https://api.weather.gov/zones/forecast/" + forecast_zone in p['affectedZones'] or
                "https://api.weather.gov/zones/fire/"     + fire_zone     in p['affectedZones'] or
                "https://api.weather.gov/zones/county/"   + county_zone   in p['affectedZones']):

                alert = collections.namedtuple('alert', 'warnzone warncounty headline event')
                all_alerts.append(alert(warnzone = forecast_zone, warncounty = county_zone, headline = p['headline'], event = p['event'].replace(' ', '+')))

    except IndexError:
        pass

    return all_alerts
