from flask import Flask, render_template, make_response, session, request, redirect
import psycopg2


import os
import json

from auth import getDBCredsandConnect


# in the Procfile, we have app:app. this is looking for the file, app, with the webserver var, app. it must match.
app = Flask(__name__,template_folder="misc/templates",subdomain_matching=True)
app.config["DEBUG"] = True
version = "beta"


@app.route("/")
def mainRoute():
    resp = make_response(render_template("helloworld.html"), 200)
    return resp

@app.route("/new")
def newRoute():
    resp = make_response(render_template("mainpage.html"),200)
    return resp

@app.route("/", subdomain="beta")
def betaMainRoute():
    resp = make_response(render_template("helloworld.html"), 200)
    return "hello, you  sly dawg"

@app.route("/login", methods=["GET"])
def loginRoute():
    resp = make_response(render_template("login.html"), 200)
    return resp

@app.route("/login", methods=["POST"])
def submitLoginRoute():
    email = request.form['email']
    password = request.form['password']


if __name__ == '__main__':
    site_url = "callama.dev"
    app.config['SERVER_NAME'] = site_url
    app.run()