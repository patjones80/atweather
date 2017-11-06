
import datetime

from django.http import HttpResponse, Http404
from django.template import loader
from django.utils.safestring import mark_safe

from .dropdown_items import *
from .funcLib import *

# both menus and active are dicts that get passed into the HTML context argument

# the menus dict controls the content of the dropdown menus. in order to make the cascading work properly via the javascript that is in index.html,
# there need to be two hidden dropdowns that always contain complete state and complete location lists, respectively

# the active dict is present in order to tell the template which button (home, about, donate, learn) to highlight blue (assign a setting of 'active')

menus  = {'trails': trails, 'states': all_states, 'state_list_full': all_states, 'locations': getLocationList(), 'locations_full': getLocationList()}
active = {'active_home': '', 'active_about': '', 'active_learn': '', 'active_disclaimer': ''}

def index(request):

	# home page
	
	template = loader.get_template('atwx1/index.html')

	actives  = {**active, **{'active_home':'active'}}
	context  = {**menus, **actives}
	
	return HttpResponse(template.render(context, request))

def about(request):

	# about page
	
	template = loader.get_template('atwx1/about.html')
	
	actives  = {**active, **{'active_about':'active'}}
	context  = {**menus, **actives}
	
	return HttpResponse(template.render(context, request))

def disclaimer(request):

	# disclaimer
	
	template = loader.get_template('atwx1/disclaimer.html')
	
	actives  = {**active, **{'active_home':'active'}}
	context  = {**menus, **actives}
	
	return HttpResponse(template.render(context, request))
	
def learn(request, learn_topic = None):

	# render the learning topics menu
	# we pick out the correct topic template to render based on the URL parameter
	
	topics = {'precip_discussion':'learn_interpret.html',
			  'wind_chill':'learn_wind_chill.html',
			  'lapse_rate':'learn_lapse_rate.html',
			  'weather_prediction':'learn_nwp.html'}

	if not learn_topic:
		template = loader.get_template('atwx1/learn_menu.html')
	else:
		template = loader.get_template('atwx1/{}'.format(topics[learn_topic]))
	
	actives  = {**active, **{'active_learn':'active'}}
	context  = {**menus, **actives}
	
	return HttpResponse(template.render(context, request))

def server_error(request):

	# handle server 500 errors
	# TODO: error handling needs fine-tuning (need to properly handle 400 and 500 separately?)
	
	template = loader.get_template('500.html')

	actives  = {**active, **{'active_learn':'active'}}
	context  = {**menus, **actives}

	return HttpResponse(template.render(context, request))
	
def forecast(request):

	# main forecast display view 
	
	locationID = int(request.GET.get('myShelter', ''))
	location   = getLocationList()[locationID]
	
	d = GetForecast(location.Latitude, location.Longitude)
	
	try:
		# we need to use mark_safe because GetForecast is basically just returning an HTML snippet, and it has to be escaped

		context = {'forecast':   	mark_safe(d['forecast']),
				   'alerts': 		GetAlerts(location.Latitude, location.Longitude), 
				   'locationName': 	location.Name}

	except KeyError:
	
		# if GetForecast encountered an exception, then it will return an error message; also use mark_safe here
		
		write_error(location, locationID)
		context = {'err_msg' : mark_safe(d['error'])}
	
	actives  = {**active,  **{'active_home':'active'}}
	context  = {**context, **menus, **actives}
	
	# keep state and location dropdowns filtered if the user selected a trail
	
	myTrail = request.GET.get('myTrail', '')
	
	if myTrail:
		context['states'] 	 = [L for L in all_states if L[3] == myTrail]
		context['locations'] = {k:v for (k,v) in getLocationList().items() if v.Trail == myTrail}
		
	# keep location dropdown filtered if the user selected a state
	
	if request.GET.get('myState', ''):
		context['locations'] = {k:v for (k,v) in getLocationList().items() if v.State == request.GET.get('myState', '')}
	
	template = loader.get_template('atwx1/forecast.html')
	
	return HttpResponse(template.render(context, request))
	
def write_error(location, locationID):

	# if GetForecast fails to return a forecast for the selected location, then log the failure occurence
	
	if os.name == 'posix':
		strfile = r'{}/api_error_log.txt'.format(CURR_DIR)
	else:
		strfile = r'{}\api_error_log.txt'.format(CURR_DIR)
	
	curtime = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
	
	with open(strfile, 'a') as f:
		f.write('{}\t{}\t{}\t{}\t{}\n'.format(curtime, locationID, location.Name, location.Latitude, location.Longitude))
		
	f.close()
