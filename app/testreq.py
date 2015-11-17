
import requests

print(requests.__version__)

#requests.get('http://forecast.weather.gov/MapClick.php?lon=-84.2476&lat=34.5627&unit=0&lg=english&FcstType=text&TextType=1', timeout=0.01, proxies={'https':'https://1.1.1.1'})
requests.get('http://www.google.com', timeout=0.01, proxies={'https':'https://1.1.1.1'})


