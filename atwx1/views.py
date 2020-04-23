
import django

from django.http import HttpResponse, HttpResponseNotFound
from django.template import loader
from django.utils.safestring import mark_safe

from .dropdown_items import *
from .function_library import *
from datetime import datetime

# both menus and active are dicts that get passed into the HTML context argument

# the menus dict controls the content of the dropdown menus. in order to make the cascading work properly via the javascript that is in index.html,
# there need to be two hidden dropdowns that always contain complete state and complete location lists, respectively

# the active dict is present in order to tell the template which button (home, about, donate, learn) to highlight blue (assign a setting of 'active')

v = django.VERSION
ver = '{}.{}.{}'.format(v[0], v[1], v[2])

menus  = {'trails': trails, 'states': all_states, 'state_list_full': all_states, 'locations': get_location_list(), 'locations_full': get_location_list(), 'django_version': ver}
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
	
	topics = {'precip_discussion': 'learn_interpret.html',
			  'wind_chill': 'learn_wind_chill.html',
			  'lapse_rate': 'learn_lapse_rate.html',
			  'weather_prediction': 'learn_nwp.html',
			  'no_forecast': 'learn_no_forecast.html'}

	if not learn_topic:
		template = loader.get_template('atwx1/learn_menu.html')
	else:
		template = loader.get_template('atwx1/{}'.format(topics[learn_topic]))
	
	actives  = {**active, **{'active_learn':'active'}}
	context  = {**menus, **actives}
	
	return HttpResponse(template.render(context, request))

def http_500(request, *args, **kwargs):
	# handle http 500 errors
	
	err_msg_top = 'AT Weather seems to be having a case of the Mondays. We aren\'t sure what\'s going on.'
	err_msg_btm = 'Please check the URL that you\'re using, and try your request again later!'

	template = loader.get_template('http_error.html')

	actives  = {**active, **{'active_home':'active', 'err_msg_top': err_msg_top, 'err_msg_btm': err_msg_btm }}
	context  = {**menus, **actives}
	
	return HttpResponse(template.render(context, request))
	
def http_404(request, *args, **kwargs):
	# handle http 404 errors
	
	err_msg_top = 'AT Weather doesn\'t have the page that you\'re looking for.'
	err_msg_btm = 'Please make sure that you are using a valid URL and forecast location, then try again.'

	template = loader.get_template('http_error.html')

	actives  = {**active, **{'active_home':'active', 'err_msg_top': err_msg_top, 'err_msg_btm': err_msg_btm }}
	context  = {**menus, **actives}
	
	return HttpResponse(template.render(context, request))

def forecast(request):
	# main forecast display view 
	
	try:
		location_id = int(request.GET.get('myShelter', ''))
		location    = get_location_list()[location_id]

	except KeyError:
		return http_404(request)	
		
	try:
		d = get_forecast(location.latitude, location.longitude)
		
		# we need to use mark_safe because GetForecast is basically just returning an HTML snippet, and it has to be escaped
		context = {'forecast': mark_safe(d['forecast']),
				   'alerts'  : get_alerts(location.latitude, location.longitude), 
				   'location_name': location.name, 'location_state': location.state, 'location_trail': location.trail, 'prev_location': location_id - 1, 'next_location': location_id + 1}
		
		template = loader.get_template('atwx1/forecast.html')
		
	except KeyError:
		# if get_forecast encountered an exception, then it will return an error message
		
		write_error(location, location_id)
		context = {'err_msg': 'There is no forecast available right now for the location you selected.'}
		template = loader.get_template('atwx1/no_forecast.html')	
	
	actives  = {**active,  **{'active_home':'active'}}
	context  = {**context, **menus, **actives}
	
	# keep state and location dropdowns filtered if the user selected a trail
	
	myTrail = request.GET.get('myTrail', '')
	
	if myTrail:
		context['states'] 	 = [L for L in all_states if L[3] == myTrail]
		context['locations'] = {k:v for (k,v) in get_location_list().items() if v.trail == myTrail}
		
	# keep location dropdown filtered if the user selected a state
	
	if request.GET.get('myState', ''):
		context['locations'] = {k:v for (k,v) in get_location_list().items() if v.state == request.GET.get('myState', '')}
	
	return HttpResponse(template.render(context, request))			
	
def write_error(location, location_id):
	''' if GetForecast fails to return a forecast for the selected location, 
	    then log the failure occurence
	'''
	
	if os.name == 'posix':
		strfile = r'{}/api_error_log.txt'.format(CURR_DIR)
	else:
		strfile = r'{}\api_error_log.txt'.format(CURR_DIR)
	
	curtime = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now())
	
	with open(strfile, 'a') as f:
		f.write('{}\t{}\t{}\t{}\t{}\n'.format(curtime, location_id, location.name, location.latitude, location.longitude))
		
	f.close()

