''' Handles the interface between URL endpoints and HTML templates
    for AT Weather.
    
    Pat Jones 
    Dec 2024
'''

from datetime import datetime
import os

import django
from django.http import HttpResponse
from django.template import loader
from django.utils.safestring import mark_safe

from .function_library import get_location_list, move, get_forecast, get_forecast_by_scraping, get_alerts

TEST_HTTP_500 = False
TEST_HTTP_404 = False
TEST_DATA_ERR = False

USE_NWS_API = True
CURR_DIR = os.path.dirname(os.path.abspath( __file__ ))

# Both menus and active are dicts that get passed into the HTML context argument

# The menus dict controls the content of the dropdown menus. in order to make the cascading work properly via the
# javascript that is in index.html, there need to be two hidden dropdowns that always contain complete state and
# complete location lists, respectively

# The active dict is present in order to tell the template which button (home, about, donate, learn) to highlight blue
# (assign a setting of 'active')

version = django.VERSION
VERSION_STR = f'{version[0]}.{version[1]}.{version[2]}'

all_locations = get_location_list()

TRAILS = [['AT' ,'Appalachian Trail', ''], ['PCT','Pacific Crest Trail', '']]
ALL_STATES = [['GA', 'AT - Georgia',        '', 'AT'],
              ['NC', 'AT - North Carolina', '', 'AT'],
              ['TN', 'AT - Tennessee',      '', 'AT'],
              ['VA', 'AT - Virginia',       '', 'AT'],
              ['MD', 'AT - Maryland',       '', 'AT'],
              ['PA', 'AT - Pennsylvania',   '', 'AT'],
              ['NJ', 'AT - New Jersey',     '', 'AT'],
              ['NY', 'AT - New York',       '', 'AT'],
              ['CT', 'AT - Connecticut',    '', 'AT'],
              ['MA', 'AT - Massachusetts',  '', 'AT'],
              ['VT', 'AT - Vermont',        '', 'AT'],
              ['NH', 'AT - New Hampshire',  '', 'AT'],
              ['ME', 'AT - Maine',          '', 'AT'],
              ['CA', 'PCT - California',   '', 'PCT'],
              ['OR', 'PCT - Oregon',       '', 'PCT'],
              ['WA', 'PCT - Washington',   '', 'PCT']]

menus  = {'trails': TRAILS, \
          'states': ALL_STATES, \
          'state_list_full': ALL_STATES, \
          'locations': all_locations, \
          'locations_full': all_locations, \
          'django_version': VERSION_STR}

active = {'active_home': '', 'active_about': '', 'active_other': '', 'active_learn': '', 'active_disclaimer': ''}

def index(request):
    ''' Home page, all other templates expand off this
    '''
    template = loader.get_template('atwx1/index.html')

    actives  = {**active, **{'active_home':'active'}}
    context  = {**menus, **actives}

    return HttpResponse(template.render(context, request))

def about(request):
    ''' Expands off the home (index) page, talking about AT Weather
    '''
    template = loader.get_template('atwx1/about.html')

    actives  = {**active, **{'active_about':'active'}}
    context  = {**menus, **actives}

    return HttpResponse(template.render(context, request))

def other(request):
    ''' Links to other weather resources for the trail
    '''
    template = loader.get_template('atwx1/other_resources.html')

    actives  = {**active, **{'active_other':'active'}}
    context  = {**menus, **actives}

    return HttpResponse(template.render(context, request))

def url_changes(request):
    ''' Discussion regarding recent changes to the URL structure of the site
    '''
    template = loader.get_template('atwx1/url_changes.html')

    actives  = {**active, **{'active_other':'active'}}
    context  = {**menus, **actives}

    return HttpResponse(template.render(context, request))

def disclaimer(request):
    ''' Disclaimer to protect my ass
    '''
    template = loader.get_template('atwx1/disclaimer.html')

    actives  = {**active, **{'active_home':'active'}}
    context  = {**menus, **actives}

    return HttpResponse(template.render(context, request))

def learn(request, learn_topic=None):
    ''' Render the learning topics menu
        We pick out the correct topic template to render based on the URL parameter
    '''
    topics = {'precip_discussion': 'learn_interpret.html', \
              'wind_chill': 'learn_wind_chill.html', \
              'lapse_rate': 'learn_lapse_rate.html', \
              'weather_prediction': 'learn_nwp.html', \
              'no_forecast': 'learn_no_forecast.html'}

    if not learn_topic:
        template = loader.get_template('atwx1/learn_menu.html')
    else:
        template = loader.get_template(f'atwx1/{topics[learn_topic]}')

    actives  = {**active, **{'active_learn':'active'}}
    context  = {**menus, **actives}

    return HttpResponse(template.render(context, request))

def http_500(request):
    ''' Handle HTTP 500 errors
    '''
    err_msg_header = 'No weather here!'
    err_msg_top = 'Sorry about that. Like the weather, technology can be unpredictable.'
    err_msg_btm = 'This is a good excuse to have a trail snack and try again later.'

    template = loader.get_template('http_error.html')

    actives  = {**active, **{'active_home':'active', \
                             'err_msg_header': mark_safe(err_msg_header), \
                             'err_msg_top': mark_safe(err_msg_top), \
                             'err_msg_btm': mark_safe(err_msg_btm)}}

    context  = {**menus, **actives}
    return HttpResponse(template.render(context, request))

def http_404(request, exception):
    ''' Handle HTTP 404 errors
    '''
    err_msg_header = 'Blerg!'
    err_msg_top = 'That page isn\'t a thing.'
    err_msg_btm = 'Please note that the URLs for forecasts have changed. Try selecting from the drop-down menus to find your forecast. If that doesn\'t work, \
                   please send me a quick note at <b>patjones80@gmail.com</b> and I\'ll get right on it.'

    template = loader.get_template('http_error.html')

    actives  = {**active, **{'active_home':'active', \
                             'err_msg_header': mark_safe(err_msg_header), \
                             'err_msg_top': mark_safe(err_msg_top), \
                             'err_msg_btm': mark_safe(err_msg_btm)}}

    context  = {**menus, **actives}
    return HttpResponse(template.render(context, request))

def forecast(request):
    ''' Main forecast display view
    '''
    try:
        location_id = request.GET.get('location_id', '')
        location    = all_locations[location_id]

        # HTTP 500 error testing
        if TEST_HTTP_500:
            return http_500(request)

    except KeyError:
        return http_404(request)

    context = {
               'location_name'  : location.name,
               'location_state' : location.state,
               'location_trail' : location.trail,
               'prev_location'  : move(all_locations, location_id=location_id, requested_dir=-1),
               'next_location'  : move(all_locations, location_id=location_id, requested_dir=1)
              }

    actives  = {**active,  **{'active_home':'active'}}
    context  = {**context, **menus, **actives}

    context['locations'] = {k: v for (k, v) in all_locations.items() if v.state == context['location_state']}

    try:
        if USE_NWS_API:
            # API option
            forecast = get_forecast(location.latitude, location.longitude)
        else:
            # HTML scraping option
            forecast = get_forecast_by_scraping(location.latitude, location.longitude)

        # We need to use mark_safe because the HTML scraping option is basically
        # just returning an HTML snippet, and it has to be escaped
        context['forecast'] = mark_safe(forecast)
        template = loader.get_template('atwx1/forecast.html')

        if TEST_DATA_ERR:
            raise Exception("Here's a test data retrieval exception")

    except Exception as e:
        # If get_forecast encountered an exception, then it will return an error message
        # that we can write to the log
        write_error(location, location_id, e)

        # Use a prettier message for the site though
        context['err_msg'] ="It looks like we\'re having trouble getting data from the National Weather \
                             Service. These things usually clear up faster than a passing rain shower."

        template = loader.get_template('atwx1/no_forecast.html')
        return HttpResponse(template.render(context, request))

    try:
        # Do alerts separately so that if there's a problem getting them, we
        # can log the problem and still return the forecast
        context['alerts'] = get_alerts(location.latitude, location.longitude)

    except Exception as e:
        write_error(location, location_id, e)

    return HttpResponse(template.render(context, request))

def write_error(location, location_id, msg):
    ''' If get_forecast fails to return a forecast for the selected location,
        then log the failure occurence
    '''
    strfile = f'{CURR_DIR}\\api_error_log.txt'

    if os.name == 'posix':
        strfile = f'{CURR_DIR}/api_error_log.txt'

    curtime = f'{datetime.now():%Y-%m-%d %H:%M:%S}'

    with open(strfile, 'a', encoding='utf-8') as f:
        f.write(f'{curtime}\t{location_id}\t{location.name}\t{location.latitude}\t{location.longitude}\t{msg}\n')
