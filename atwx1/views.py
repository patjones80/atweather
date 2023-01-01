
import django

from django.http import HttpResponse, HttpResponseNotFound
from django.template import loader
from django.utils.safestring import mark_safe

from .function_library import *
from datetime import datetime

TEST_HTTP_500 = True
TEST_HTTP_404 = False
TEST_DATA_ERR = False

# Both menus and active are dicts that get passed into the HTML context argument

# The menus dict controls the content of the dropdown menus. in order to make the cascading work properly via the 
# javascript that is in index.html, there need to be two hidden dropdowns that always contain complete state and 
# complete location lists, respectively

# The active dict is present in order to tell the template which button (home, about, donate, learn) to highlight blue 
# (assign a setting of 'active')

v = django.VERSION
ver = f'{v[0]}.{v[1]}.{v[2]}'

TRAILS = [['AT' ,'Appalachian Trail',''], ['PCT','Pacific Crest Trail','']]
ALL_STATES = [['GA','AT - Georgia',       '','AT'],
              ['NC','AT - North Carolina','','AT'],
              ['TN','AT - Tennessee',     '','AT'],
              ['VA','AT - Virginia',      '','AT'],
              ['MD','AT - Maryland',      '','AT'],
              ['PA','AT - Pennsylvania',  '','AT'],
              ['NJ','AT - New Jersey',    '','AT'],
              ['NY','AT - New York',      '','AT'],
              ['CT','AT - Connecticut',   '','AT'],
              ['MA','AT - Massachusetts', '','AT'],
              ['VT','AT - Vermont',       '','AT'],
              ['NH','AT - New Hampshire', '','AT'],
              ['ME','AT - Maine',         '','AT'],
              ['CA','PCT - California',  '','PCT'],
              ['OR','PCT - Oregon',      '','PCT'],
              ['WA','PCT - Washington',  '','PCT']]
  
menus  = {'trails': TRAILS, \
          'states': ALL_STATES, \
          'state_list_full': ALL_STATES, \
          'locations': get_location_list(), \
          'locations_full': get_location_list(), \
          'django_version': ver}
          
active = {'active_home': '', 'active_about': '', 'active_learn': '', 'active_disclaimer': ''}

def index(request):
    # Home page   
    template = loader.get_template('atwx1/index.html')

    actives  = {**active, **{'active_home':'active'}}
    context  = {**menus, **actives}
    
    return HttpResponse(template.render(context, request))

def about(request):
    # About page   
    template = loader.get_template('atwx1/about.html')
    
    actives  = {**active, **{'active_about':'active'}}
    context  = {**menus, **actives}
    
    return HttpResponse(template.render(context, request))

def disclaimer(request):
    # Disclaimer  
    template = loader.get_template('atwx1/disclaimer.html')
    
    actives  = {**active, **{'active_home':'active'}}
    context  = {**menus, **actives}
    
    return HttpResponse(template.render(context, request))
    
def learn(request, learn_topic = None):
    # Render the learning topics menu
    # We pick out the correct topic template to render based on the URL parameter
    
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

def http_500(request, *args, **kwargs):
    # Handle HTTP 500 errors
    err_msg_header = 'Blerg!'
    err_msg_top = 'We can\'t get what you\'re looking for right now. Sorry about that.'
    err_msg_btm = 'The weather\'s always changing around here, so try again later.'

    template = loader.get_template('http_error.html')

    actives  = {**active, **{'active_home':'active', \
                             'err_msg_header': mark_safe(err_msg_header), \
                             'err_msg_top': mark_safe(err_msg_top), \
                             'err_msg_btm': mark_safe(err_msg_btm)}}

    context  = {**menus, **actives}    
    return HttpResponse(template.render(context, request))

def http_404(request, *args, **kwargs):
    # Handle HTTP 404 errors
    err_msg_header = 'No weather here!'
    err_msg_top = 'That page isn\'t a thing.'
    err_msg_btm = 'Try selecting from the drop-down menus to find your forecast. If that doesn\'t work, \
                   please send me a quick note at <b>patjones80@gmail.com</b> and I\'ll get right on it.'

    template = loader.get_template('http_error.html')

    actives  = {**active, **{'active_home':'active', \
                             'err_msg_header': mark_safe(err_msg_header), \
                             'err_msg_top': mark_safe(err_msg_top), \
                             'err_msg_btm': mark_safe(err_msg_btm)}}    

    context  = {**menus, **actives}
    return HttpResponse(template.render(context, request))

def forecast(request):
    # Main forecast display view 
    try:
        location_id = int(request.GET.get('myShelter', ''))
        location    = get_location_list()[location_id]

        # HTTP 500 error testing
        if TEST_HTTP_500:
            return http_500(request)

    except KeyError:
        return http_404(request)    

    try:
        # API option
        # d = get_forecast(location.latitude, location.longitude)
        
        # HTML scraping option
        forecast = get_forecast_by_scraping(location.latitude, location.longitude)
        
        # We need to use mark_safe because GetForecast is basically just returning an HTML snippet, 
        # and it has to be escaped
        
        # context = {'forecast': mark_safe(d['forecast']),  
        
        context = {'forecast': mark_safe(forecast), \
                   'alerts'  : get_alerts(location.latitude, location.longitude), \
                   'location_name': location.name, \
                   'location_state': location.state, \
                   'location_trail': location.trail, \
                   'prev_location': location_id - 1, \
                   'next_location': location_id + 1}

        template = loader.get_template('atwx1/forecast.html')
        
        if TEST_DATA_ERR:
            raise Exception("Here's a test data retrieval exception")
        
    except Exception as e:
        # If get_forecast encountered an exception, then it will return an error message        
        write_error(location, location_id, e)

        context = {'err_msg': "It looks like we\'re having trouble getting data from the National Weather \
                               Service. These things usually clear up faster than a passing rain shower."}

        template = loader.get_template('atwx1/no_forecast.html')    

    actives  = {**active,  **{'active_home':'active'}}
    context  = {**context, **menus, **actives}
    
    # Keep state and location dropdowns filtered if the user selected a trail    
    myTrail = request.GET.get('myTrail', '')
    
    if myTrail:
        context['states'] = [L for L in ALL_STATES if L[3] == myTrail]
        context['locations'] = {k:v for (k,v) in get_location_list().items() if v.trail == myTrail}
        
    # Keep location dropdown filtered if the user selected a state
    if request.GET.get('myState', ''):
        context['locations'] = {k:v for (k,v) in get_location_list().items() if v.state == request.GET.get('myState', '')}

    return HttpResponse(template.render(context, request))

def write_error(location, location_id, msg):
    ''' If get_forecast fails to return a forecast for the selected location, 
        then log the failure occurence
    '''
    if os.name == 'posix':
        strfile = f'{CURR_DIR}/api_error_log.txt'
    else:
        strfile = f'{CURR_DIR}\\api_error_log.txt'

    curtime = f'{datetime.now():%Y-%m-%d %H:%M:%S}'
    
    with open(strfile, 'a') as f:
        f.write(f'{curtime}\t{location_id}\t{location.name}\t{location.latitude}\t{location.longitude}\t{msg}\n')
        
    f.close()

