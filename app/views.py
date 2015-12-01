
# laptop dev path:  c:/Python34/atweather

from flask import render_template, request
from app import app

import requests

def get_html(url):

    # return the HTML that sources the URL passed into the function
    # the proxies argument is required for the production version of the code on PythonAnywhere's server

    page = requests.get(url) #, proxies = {'http':'http://proxy.server:3128'})
    html_string = page.text

    return html_string

def write_nws_html(url):

    # write the HTML for the text forecast to nws.html, which will "extend" the base HTML file index.html
    html_string = get_html(url)

    # minor formatting adjustment(s)
    html_string = html_string.replace('<b>Last Update: </b></a>','<b>Last Update</b></a>: ')
    html_string = html_string.replace('margin-left:-40px;','')
    html_string = html_string.replace('font-family: Arial !important', 'font-family: \'Trebuchet MS\', Helvetica, sans-serif')
    html_string = html_string.replace('<br>&nbsp;', ', ')

    # the watch/warning/hazardous weather links all point to a PHP script on the NWS page; these links don't work from an external HTML source unless appended like this:
    html_string = html_string.replace('showsigwx.php','http://forecast.weather.gov/showsigwx.php')

    f = open('c:/Python34/atweather/app/templates/nws.html', 'w')

    f.write('{% extends "index.html" %}\n{% block forecast %}\n' + html_string + '\n{% endblock %}')
    f.close()

def init_shelter_list():

    # pull the shelters and URLs into a list and return it for initialization

    L = []

    f = open('c:/Python34/atweather/at_shelter_list.txt', 'r')

    for line in f:
        L.append([int(line.split('\t')[0]), line.split('\t')[1], line.split('\t')[2], line.split('\t')[5].rstrip(), line.split('\t')[6], ''])

    f.close()

    return L

# home page

@app.route('/')
def index():

    return render_template('index.html', shelter_list = init_shelter_list(), shelter_list_full = init_shelter_list())

# probability of precipitation (pop) discussion

@app.route('/precip_discussion')
def pop_discussion():

    return render_template('pop_discussion.html', shelter_list = init_shelter_list(), shelter_list_full = init_shelter_list())

# something from the shelter list was selected

@app.route('/forecast/loc_id=<int:loc_id>', methods = ['GET','POST'])
def forecast(loc_id = None):

    L = init_shelter_list()
    
    if request.method == 'GET':
        
        if loc_id:
            url = L[loc_id-1][3]
            write_nws_html(url)
            
            for s in L:
                if s[0] == loc_id:
                    s[3] = 'selected'

            return render_template('nws.html', shelter_list = [s for s in L if s[4] == L[loc_id-1][4]], selected_state = L[loc_id-1][4], shelter_list_full = init_shelter_list())

