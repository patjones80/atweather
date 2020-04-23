# Appalachian Trail Weather

This repo contains the codebase for the website www.atweather.org

## About

Appalachian Trail Weather is a simple Django front end for the National Weather Service (NOAA) weather forecast API. It enables users to select a location from a pre-defined list and obtain the NWS weather forecast for that location by mapping each location to a pair of lat/lon coordinates, and passing those to the relevant API endpoint. See [api.weather.gov](https://api.weather.gov)
Example API calls:

* [https://api.weather.gov/points/34.63,-84.19/forecast](https://api.weather.gov/points/34.63,-84.19/forecast) - Call forecast endpoint on latitude = 34.63N, longitude = 84.19W
* [https://api.weather.gov/alerts/active/zone/NCZ033](https://api.weather.gov/alerts/active/zone/NCZ033) - Call weather alerts endpoint on forecast zone NCZ033
* [https://api.weather.gov/points/36.12,-82.05](https://api.weather.gov/points/36.12,-82.05) - Metadata endpoint for latitude = 34.63N, longitude = 84.19W

## Built With

Python 3 and Django

## Creator/Maintainer

Patrick Jones [patjones80@gmail.com](mailto:patjones80@gmail.com)

## Acknowledgments

Grateful to Jeff Erickson and Adam Louie for assistance in the project's early days (2014/15) with server side conceptualization and CSS respectively.
