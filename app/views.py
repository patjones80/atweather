
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


@app.route('/changes_discussion')

def changes_discussion():

    return render_template('changes_discussion.html', **context_default)

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
        
    # retain trail selection
    
    trail_list = dropdown_items.trails[:]   

#    mark_selected(trail_list, loc_trail, 2)
    
    # retain selection of state or park name
    
    if loc_trail   == 'AT':        
        state_list = dropdown_items.states_at[:]
        
    elif loc_trail == 'PCT':
        state_list = dropdown_items.states_pct[:]

    elif loc_trail == 'NP':
        state_list = dropdown_items.states_np[:]
        
    else:
        state_list = dropdown_items.all_states[:]
    
#    mark_selected(state_list, loc_state, 2)

    # keep location list filtered 
    
    loc_list = list(LOCATIONS.values())[:]
        
    state_abbr = tuple(M[0] for M in state_list)
            
    if loc_state:
        
        # user filtered by state
        loc_list = [s for s in loc_list if s[4] == loc_state]
        
    elif loc_trail:
        
        # user only filtered by trail
        loc_list = [s for s in loc_list if s[4] in state_abbr]
    
    # save location

    for item in loc_list:

        print(item)
        
        if item[0] == loc_id:
            location_to_display = 'Selected location: ' + item[1]

    context = { 'trail_list':      trail_list,
                'state_list':      state_list,
                'state_list_full': dropdown_items.all_states,
                'shelter_list':      loc_list,
                'shelter_list_full': list(LOCATIONS.values()),
                'location_selected': location_to_display}

    fcstLocation = funcLib.Location(curr_id = loc_id)
    
    return render_template('index.html', forecast_text = Markup(funcLib.getForecast(fcstLocation.Latitude, fcstLocation.Longitude)), **context)    


    # this is in preparation for the arrival of the new NWS API; see NWS API reference for structure of returned JSON
    
##    forecast = funcLib.getForecast(fcstLocation.Latitude, fcstLocation.Longitude) #['properties']['periods']
##
##    if isinstance(forecast, str):
##        return render_template('index.html', err_msg = forecast, **context)
##    else:
##        return render_template('index.html', forecast = forecast['properties']['periods'], location_to_display = location_to_display, **context)


@app.errorhandler(404)

def page_not_found(e):
    
    return render_template('404.html', **context_default)


def mark_selected(L, selected_item, select_column):

    '''
    Deprecated as of December 2016 update.

    At different points, we want a selection from a dropdown list to remain selected when the template gets rendered. Since
    each call of render_template does this, we need to have a function that we can pass a dropdown list into with the item
    that the user selected, and ensure that the 'selected' marker gets attached to the dropdown list in question when we pass
    it back to the client for rendering.

    This is cumbersome, but the best I can come up with right now.

    '''

    for item in L:
        if item[0] == selected_item:
            item[select_column] = 'selected'
        else:
            item[select_column] = ''
            
# pull the full location list just once

LOCATIONS = funcLib.getLocationList()

# construct the default list of template arguments

context_default = { 'trail_list':      dropdown_items.trails[:],
                    'state_list':      dropdown_items.all_states[:],
                    'state_list_full': dropdown_items.all_states,
                    'shelter_list':      list(LOCATIONS.values())[:],
                    'shelter_list_full': list(LOCATIONS.values()) }            
