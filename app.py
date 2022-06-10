from flask import Flask, render_template, make_response, session, request, redirect
import psycopg2

import os
import json



# in the Procfile, we have app:app. this is looking for the file, app, with the webserver var, app. it must match.
app = Flask(__name__,template_folder="misc/templates",subdomain_matching=True)
app.config["DEBUG"] = True

@app.route("/")
def mainRoute():
    resp = make_response(render_template("helloworld.html"), 200)
    return resp

@app.route("/", subdomain="beta")
def betaMainRoute():
    resp = make_response(render_template("helloworld.html"), 200)
    return "hello, you  sly dawg"



if __name__ == '__main__':
    site_url = "callama.dev"
    app.config['SERVER_NAME'] = site_url
    app.run()