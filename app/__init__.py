
from flask import Flask, render_template

app = Flask(__name__)

from app import views

@app.errorhandler(404)

def page_not_found(e):
    
    return render_template("404.html")
