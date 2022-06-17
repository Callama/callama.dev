# Doc String Formatting: https://betterprogramming.pub/how-to-write-proper-docstrings-for-a-python-function-7c40b8d2e153#

from flask import Flask, render_template, make_response, session, request, redirect
import psycopg2


import os
import json

from database_func import getDBCredsandConnect, createUserCache


# in the Procfile, we have app:app. this is looking for the file, app, with the webserver var, app. it must match.
app = Flask(__name__,template_folder="misc/templates",subdomain_matching=True)
app.config["DEBUG"] = True

def start():
    version = "prod"

    global dbConn
    dbConn = getDBCredsandConnect(type=version)
    # make caches for faster response times
        
start()
import auth



    


@app.route("/")
def mainRoute():
    resp = make_response(render_template("helloworld.html"), 200)
    return resp

@app.route("/new")
def newRoute():
    resp = make_response(render_template("mainpage.html"),200)
    return resp

@app.route("/", subdomain="beta",methods=["GET"])
def betaMainRoute():
    resp = make_response(render_template("mainpage.html"),200)
    return resp






if __name__ == '__main__':
    app.config['SERVER_NAME'] = "callama.dev:443"
    app.run()