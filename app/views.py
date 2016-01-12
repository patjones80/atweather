
"""
views.py

Implements the views module necessary for development with
the Flask web framework.

"""

import os
import requests

from flask import render_template, request, Markup
from app   import app

# define the parent directory for the project so that we don't need absolute file paths

PARENT_DIR = os.path.join(os.path.dirname(__file__), '..')

# pull the full location list just once

LOCATIONS = []

with open('%s/at_shelter_list.txt' % PARENT_DIR, 'r') as LocationFile:

    for line in LocationFile:
        cols = line.split('\t')

        # location id, location name, NOAA URL, state abbreviation, placeholder for selected tag
        LOCATIONS.append([int(cols[0]), cols[1], cols[5].rstrip(), cols[6].rstrip('\n'), ''])

print(__doc__)

def get_html(url):

    """

    The full NOAA weather forecast URL for each location is stored in
    LOCATIONS, which in turn is sourced from at_shelter_list.txt (see above).

    We submit this URL to NOAA and pull the HTML for their text-only
    weather forecast, which we use for display of the forecast on atweather.

    If something goes wrong, NOAA returns a '404 Not Found', which we check
    for. If there are any other problems, we check for a general exception. In
    either case, we return False so that an error can be displayed.

    """

    exception_thrown = False

    # return the HTML that sources the URL passed into the function
    # the proxies argument is required for PythonAnywhere's server

    try:

        page = requests.get(url) #, proxies = {'http':'http://proxy.server:3128'})
        html_string = page.text

    except requests.exceptions.RequestException:

        exception_thrown = True

    # formatting changes to what we are bringing in from NOAA (listed in the text file shown)

    with open('%s/formatting_adjustments.txt' % PARENT_DIR, 'r') as format_changes:
        for line in format_changes:
            html_string = html_string.replace(line.split('\t')[0], line.split('\t')[1])

    # the links to hazardous weather warnings embedded in the NOAA page don't work unless
    # replaced with the absolute URL

    html_string = html_string.replace('showsigwx.php', 'http://forecast.weather.gov/showsigwx.php')

    if html_string.find('404 Not Found') >= 0 or exception_thrown:
        return False
    else:
        return html_string

@app.route('/')

def index():

    """
    Handles rendering of the home page

    """

    return render_template('index.html', shelter_list = LOCATIONS,
                           shelter_list_full = LOCATIONS)

@app.route('/precip_discussion')

def pop_discussion():

    """
    Handles rendering of the probability of precipitation discussion

    """

    return render_template('pop_discussion.html', shelter_list = LOCATIONS,
                           shelter_list_full = LOCATIONS)

@app.route('/forecast', methods = ['GET'])

def forecast(loc_id = None):

    """
    Handles rendering of page after a location has been selected

    """

    loc_state = request.args['myState']
    loc_id = int(request.args['myShelter'])

    shelter_list = LOCATIONS

    if loc_id:

        # label this element in the list as selected so that it stays selected on re-render
        shelter_list[loc_id - 1][4] = 'selected'

        # URL to submit to NOAA
        url = shelter_list[loc_id - 1][2]

        # if the user filtered the state list, make sure it stays filtered on re-render
        if len(loc_state) > 0:
            shelter_list = [s for s in shelter_list if s[3] == loc_state]

        if get_html(url) is False:
            return render_template('404_NOAA.html', shelter_list = shelter_list,
                                   shelter_list_full = LOCATIONS)
        else:
            return render_template('index.html', shelter_list = shelter_list,
                                   shelter_list_full = LOCATIONS,
                                   forecast_text = Markup(get_html(url)))

