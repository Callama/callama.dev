import requests
import os

from app import app
from flask import Flask, render_template, make_response, session, request, redirect


def verifyCredentials(session, email, password):
    ...


def getDBCredsandConnect(session,type="beta"):
    # when it is being ran on an enviroment that is not heroku
    if type == "beta":
        api_key = os.environ['heroku_api_key']

    if type == "prod":
       api_key = os.environ['api_key']

    req = requests.get("https://api.heroku.com/apps/callamadev/config-vars",headers={"Authorization": f"Bearer {api_key}", "Accept": "application/vnd.heroku+json; version=3"})
    creds = req.json()
    # remove this from the data 
    creds.pop("api_key")
   

### ROUTES ###

@app.route("/signup", methods=["GET"])
def signupRoute():
    resp = make_response(render_template("test_signup.html"), 200)
    return resp

@app.route("/signup",methods=["POST"])
def signupPostRoute():
   # email = request.form['email']
    password = request.form['password']
    username = request.form['username']
    #username = request.form['username']
    #return f"{email}, {password},{username}"
    return f"{password}"
