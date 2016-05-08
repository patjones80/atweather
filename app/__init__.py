
from flask import Flask, render_template

#from flask_sslify import SSLify

app = Flask(__name__)

#sslify = SSLify(app)

from app import views

##@app.errorhandler(404)
##
##def page_not_found(e):
##    
##    return render_template("404.html")

