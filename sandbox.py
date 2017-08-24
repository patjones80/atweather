
import requests

##BASE_URL = 'https://api.weather.gov/points/{},{}'
##
##with open(r'C:\Users\jonesp\atweather\atwx1\at_shelter_list.txt', 'r') as f:
##    for line in f:
##        lat = line.split('\t')[3]
##        lon = line.split('\t')[2]
##
##        fcst_pt = BASE_URL.format(lat, lon)
##        
##        response = requests.get(fcst_pt, headers = { "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36" }, verify = False)
##        metadata = response.json()
##
##        try:
##            zone = metadata['properties']['forecastZone']
##            print('{}: {}'.format(fcst_pt, zone))
##        except KeyError:
##            print('{}: {}'.format(fcst_pt, 'metadata error'))            
##        
##f.close()

def GetForecastZone(lat, lon):
    
    response = requests.get('https://api.weather.gov/points/{},{}'.format(lat, lon),
                             headers = { "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36" },
                             verify = True)

    metadata = response.json()
    zone = metadata['properties']['forecastZone'].split('/')[5]

    return zone

def GetFireZone(lat, lon):
    
    response = requests.get('https://api.weather.gov/points/{},{}'.format(lat, lon),
                             headers = { "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36" },
                             verify = True)

    metadata = response.json()
    zone = metadata['properties']['fireWeatherZone'].split('/')[5]

    return zone


response = requests.get('https://api.weather.gov/alerts/active/zone/{}'.format(GetFireZone(42.14703, -121.72548)),
                         headers = { "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36" },
                         verify  = True)

alerts   = response.json()

try:
    headline = alerts['features'][0]['properties']['headline']
    print(headline)
    
except IndexError:
    print('No warnings at this time.')


