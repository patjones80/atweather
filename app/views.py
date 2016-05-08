
"""
views.py

Implements the views module necessary for development with
the Flask web framework.

"""

import os
import requests

from flask import render_template, request, Markup
from app   import app

def get_locations():

    LOCATIONS = []
    
    with open('%s/at_shelter_list.txt' % PARENT_DIR, mode = 'r', encoding = 'UTF-8') as LocationFile:

        for line in LocationFile:
            cols = line.split('\t')

            # location id, location name, NOAA URL, state abbreviation, placeholder for selected tag
            LOCATIONS.append([int(cols[0]), cols[1], cols[5].rstrip(), cols[6].rstrip('\n'), ''])

    return LOCATIONS

def get_states(trail_selection = None, state_selection = None):

    states_at = [['GA','AT - Georgia','','AT'],
                 ['NC','AT - North Carolina','','AT'],
                 ['TN','AT - Tennessee','','AT'],
                 ['VA','AT - Virginia','','AT'],
                 ['MD','AT - Maryland','','AT'],
                 ['PA','AT - Pennsylvania','','AT'],
                 ['NJ','AT - New Jersey','','AT'],
                 ['NY','AT - New York','','AT'],
                 ['CT','AT - Connecticut','','AT'],
                 ['MA','AT - Massachusetts','','AT'],
                 ['VT','AT - Vermont','','AT'],
                 ['NH','AT - New Hampshire','','AT'],
                 ['ME','AT - Maine','','AT']]

    states_pct = [['CA','PCT - California','','PCT'],
                  ['OR','PCT - Oregon','','PCT'],
                  ['WA','PCT - Washington','','PCT']]

    if trail_selection == None:
        states = states_at + states_pct
    elif trail_selection == 'AT':
        states = states_at
    else:
        states = states_pct
    
    for s in states:
        if s[0] == state_selection:
            s[2] = 'selected'
        
    return states

def get_trails():

    # define the trail list

    TRAILS = []
    TRAILS = [['AT','Appalachian Trail',''],['PCT','Pacific Crest Trail','']]

    return TRAILS

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

    with open('%s/formatting_adjustments.txt' % PARENT_DIR, mode = 'r', encoding = 'ISO-8859-1') as format_changes:
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
    
    return render_template('index.html', **context_default)

@app.route('/precip_discussion')

def pop_discussion():

    """
    Handles rendering of the probability of precipitation discussion

    """

    return render_template('pop_discussion.html', **context_default)

@app.route('/forecast', methods = ['GET'])

def forecast():

    """
    Handles rendering of page after a location has been selected

    """

    (loc_state, loc_id) = (request.args['myState'], int(request.args['myShelter']))    
    (trail_list, shelter_list) = (get_trails(), get_locations())

    loc_trail = request.args.get('myTrail','AT')
    
    if loc_id:

        # retain our trail selection on re-render        
        for trail in trail_list:
            if trail[0] == loc_trail:
                trail[2] = 'selected'
            else:
                trail[2] = ''
        
        # retain our shelter/location selection on re-render        
        shelter_list[loc_id - 1][4] = 'selected'

        # URL to submit to NOAA        
        url = shelter_list[loc_id - 1][2]

        # if the user filtered the shelter list, make sure it stays filtered on re-render
        state_list = get_states(loc_trail, loc_state)
        state_abbr = tuple(M[0] for M in state_list)
            
        if loc_state:
            # user filtered by state
            shelter_list = [s for s in shelter_list if s[3] == loc_state]
        elif loc_trail:
            # user only filtered by trail
            shelter_list = [s for s in shelter_list if s[3] in state_abbr]            

        context = { 'trail_list': trail_list,
                    'state_list': state_list,
                    'state_list_full': get_states(),
                    'shelter_list': shelter_list[:],
                    'shelter_list_full': LOCATIONS }
        
        if get_html(url) is False:        
            return render_template('404_NOAA.html', **context)
        
        else:            
            return render_template('index.html', forecast_text = Markup(get_html(url)), **context)

@app.errorhandler(404)

def page_not_found(e):
    
    return render_template('404.html', **context_default)

# define the parent directory for the project so that we don't need absolute file paths

PARENT_DIR = os.path.join(os.path.dirname(__file__), '..')

# pull the full location list just once

LOCATIONS = get_locations()

# construct the default list of template arguments

context_default = { 'trail_list': get_trails(),
                    'state_list': get_states(),
                    'state_list_full': get_states(),
                    'shelter_list': LOCATIONS,
                    'shelter_list_full': LOCATIONS }

print(__doc__)
