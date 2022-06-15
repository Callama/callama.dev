# Doc String Formatting: https://betterprogramming.pub/how-to-write-proper-docstrings-for-a-python-function-7c40b8d2e153#

from flask import Flask, render_template, make_response, session, request, redirect
import psycopg2


import os
import json



# in the Procfile, we have app:app. this is looking for the file, app, with the webserver var, app. it must match.
app = Flask(__name__,template_folder="misc/templates",subdomain_matching=True)
app.config["DEBUG"] = True

import auth

def getDBCredsandConnect(type):
    """ 
    Get DB creds and connect to the databse

    :param type: str, "beta" or "prod" to dertimine how to gather DB creds

    :return: db connection object
    """
    # when it is being ran on an enviroment that is not heroku
    if type == "beta":
        api_key = os.environ['heroku_api_key']

    if type == "prod":
       api_key = os.environ['api_key']

    req = requests.get("https://api.heroku.com/apps/callamadev/config-vars",headers={"Authorization": f"Bearer {api_key}", "Accept": "application/vnd.heroku+json; version=3"})
    creds = req.json()
    # remove this from the data 
    creds.pop("api_key")
    # connect to the database using the creds we just got
    dbConn = psycopg2.connect(**creds)
    return dbConn

global dbConn
dbConn = getDBCredsandConnect(type=version)





    


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



@app.route("/login", methods=["GET"])
def loginRoute():
    resp = make_response(render_template("login.html"), 200)
    return resp



@app.route("/login", methods=["POST"])
def submitLoginRoute():
    email = request.form['email']
    password = request.form['password']


if __name__ == '__main__':
    app.config['SERVER_NAME'] = "callama.dev:443"
    app.run()