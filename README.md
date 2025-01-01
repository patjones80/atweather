
## Appalachian Trail Weather

This repo contains the codebase for the website www.atweather.org

### About

Appalachian Trail Weather is a simple Django front-end for the National Weather Service (NOAA) weather forecast API. It enables users to select a location from a pre-defined list and obtain the NWS weather forecast for that location by mapping each location to a pair of lat/lon coordinates, and passing those to the relevant API endpoint. See [API Web Service](https://www.weather.gov/documentation/services-web-api#/default/gridpoint_forecast).

Example API calls:

 - [https://api.weather.gov/points/45.1753,-121.0816](https://api.weather.gov/points/45.1753,-121.0816) - Call metadata endpoint on latitude = 45.1753N, longitude = 121.0816W

 - [https://api.weather.gov/gridpoints/PDT/53,91/forecast](https://api.weather.gov/gridpoints/PDT/53,91/forecast) - Call forecast endpoint on latitude = 45.1753N, longitude = 121.0816W (obtained in the JSON resulting from the metadata endpoint call.

 - [https://api.weather.gov/alerts/active/zone/NCZ033](https://api.weather.gov/alerts/active/zone/NCZ033) - Call weather alerts endpoint on forecast zone NCZ033

### Built With

Python 3 and Django

### Creator/Maintainer

Patrick Jones [patjones80@gmail.com](mailto:patjones80@gmail.com)

> Written with [StackEdit](https://stackedit.io/).
