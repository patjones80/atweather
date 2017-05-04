
"""
views.py

Implements the views module necessary for development with
the Flask web framework.

"""

from flask import render_template, request, Markup
from app   import app

from app import funcLib
from app import dropdown_items

@app.route('/')

def index():

    """
    Handles rendering of the home page

    """
        
    return render_template('index.html', **context_default)


@app.route('/disclaimer')

def changes_discussion():

    return render_template('disclaimer.html', **context_default)

@app.route('/precip_discussion')

def pop_discussion():

    """
    Handles rendering of the probability of precipitation discussion

    """

    return render_template('pop_discussion.html', **context_default)

@app.route('/wind_chill')

def wind_chill():

    """
    Handles rendering of the probability of precipitation discussion

    """

    return render_template('wind_chill.html', **context_default)

@app.route('/forecast', methods = ['GET'])

def forecast():

    """
    Handles rendering of page after a location has been selected

    """

    (loc_trail, loc_state, loc_id) = (request.args['myTrail'], request.args['myState'], int(request.args['myShelter']))  
    
    # keep the state list filtered after forecast selection
    
    if loc_trail   == 'AT':        
        state_list = dropdown_items.states_at
        
    elif loc_trail == 'PCT':
        state_list = dropdown_items.states_pct

    elif loc_trail == 'NP':
        state_list = dropdown_items.states_np
        
    else:
        state_list = dropdown_items.all_states

    # keep location list filtered 
    
    loc_list = [(j, LOCATIONS[j].Name, LOCATIONS[j].State) for j in LOCATIONS.keys()]
    state_abbr = tuple(M[0] for M in state_list)
            
    if loc_state:
        
        # user filtered by state
        loc_list = [t for t in loc_list if t[2] == loc_state]
        
    elif loc_trail:
        
        # user only filtered by trail
        loc_list = [t for t in loc_list if t[2] in state_abbr]
    
    # save location
    
    for item in loc_list:
        
        if item[0] == loc_id:
            location_to_display = item[1]

    context = { 'trail_list'       : dropdown_items.trails,
                'state_list'       : state_list,
                'state_list_full'  : dropdown_items.all_states,
                'shelter_list'     : loc_list,
                'shelter_list_full': T,
                'location_selected': location_to_display}

    # the requested location
    fcstLocation = LOCATIONS[loc_id]

    # the actual forecast, returned as a JSON dictionary
    forecast = funcLib.getForecast(fcstLocation.Latitude, fcstLocation.Longitude)

    if isinstance(forecast, dict):

        try:
            return render_template('index.html', forecast = forecast['properties']['periods'], location_to_display = location_to_display, **context)        
        except KeyError:
            return render_template('index.html', err_msg = 'The forecast data for this location has expired. Please check again later for an updated forecast.', **context)
            
    else:
        
        return render_template('index.html', err_msg = forecast, **context)

@app.errorhandler(404)

def page_not_found(e):
    
    return render_template('404.html', **context_default)

            
# pull the full location list just once

LOCATIONS = funcLib.getLocationList()

# construct the default list of template arguments

T = [(j, LOCATIONS[j].Name, LOCATIONS[j].State) for j in LOCATIONS.keys()]

context_default = { 'trail_list':      dropdown_items.trails,
                    'state_list':      dropdown_items.all_states,
                    'state_list_full': dropdown_items.all_states,
                    'shelter_list':      T,
                    'shelter_list_full': T }            
