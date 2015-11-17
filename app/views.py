
# laptop dev path:  c:/Python34/atweather

from flask import render_template, request
from app import app

import requests

def get_html(url):

    # return the HTML that sources the URL passed into the function

    page = requests.get(url) #, proxies = {'http':'http://proxy.server:3128'})
    html_string = page.text

    return html_string

def write_nws_html(url):

    # write the HTML for the text forecast to nws.html, which will "extend" the base HTML file index.html
    html_string = get_html(url)

    # minor formatting adjustment(s)
    html_string = html_string.replace('<b>Last Update: </b></a>','<b>Last Update</b></a>: ')
    html_string = html_string.replace('margin-left:-40px;','')

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
        L.append([int(line.split('\t')[0]), line.split('\t')[1], line.split('\t')[2], line.split('\t')[5].rstrip(), ''])

    f.close()

    return L

@app.route('/')

def index():

    # define the sort options for the list with NOBO as default
    sort_options = [('nobo','South to north (NOBO)', 'checked'),('sobo','North to south (SOBO)', ''),('atoz','Alphabetical', '')]
    
    write_nws_html('http://forecast.weather.gov/MapClick.php?lon=-84.2476&lat=34.5627&unit=0&lg=english&FcstType=text&TextType=1')
#    write_nws_html('http://google.com')

    return render_template('dropdown.html', shelter_list = init_shelter_list(), sort_options = sort_options, my_sort = 'nobo')

@app.route('/<sorting>', methods = ['GET','POST'])
@app.route('/<sorting>/forecast/loc_id=<int:loc_id>', methods = ['GET','POST'])

def forecast(sorting = 'nobo', loc_id = None):

    L = init_shelter_list()

    if request.method == 'GET':

        L_ordered = []
        sort_options = []

        # we want to retain the dropdown list sort order, whatever it happens to be coming into this function

        if sorting == 'nobo':
            L_ordered = sorted(L[:], key = lambda x: x[0], reverse = False)
            sort_options = [('nobo','South to north (NOBO)', 'checked'),('sobo','North to south (SOBO)', ''),('atoz','Alphabetical', '')]       # amicalola

        elif sorting == 'sobo':
            L_ordered = sorted(L[:], key = lambda x: x[0], reverse = True)
            sort_options = [('nobo','South to north (NOBO)', ''),('sobo','North to south (SOBO)', 'checked'),('atoz','Alphabetical', '')]       # katahdin

        elif sorting == 'atoz':
            L_ordered = sorted(L[:], key = lambda x: x[2], reverse = False)
            sort_options = [('nobo','South to north (NOBO)', ''),('sobo','North to south (SOBO)', ''),('atoz','Alphabetical', 'checked')]       # 501 shelter

        if loc_id:
            url = L[loc_id-1][3]
            write_nws_html(url)

            for s in L:
                if s[0] == loc_id:
                    s[3] = 'selected'

            return render_template('nws.html', shelter_list = L_ordered, sort_options = sort_options, my_sort = sorting)

        else:

            return render_template('dropdown.html', shelter_list = L_ordered, sort_options = sort_options, my_sort = sorting)

