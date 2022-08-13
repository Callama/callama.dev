# Doc String Formatting: https://betterprogramming.pub/how-to-write-proper-docstrings-for-a-python-function-7c40b8d2e153#

from flask import Flask, render_template, make_response, session, request, redirect
import psycopg2


import os
import json
import datetime

from cache_funcs import  createUserCache, createWebSessionsCache
import global_vars


# in the Procfile, we have app:app. this is looking for the file, app, with the webserver var, app. it must match.
app = Flask(__name__,template_folder="misc/templates")
app.config["DEBUG"] = True



def start():
    # we have an external file, global_vars, with function __init__ to initialize the DB as a global var
    # to be accesible by all modules in the app via import
    global_vars.__init__()
    global dbConn, version, userCache
    from global_vars import dbConn, version, userCache, webSessionsCache
    print(userCache)
        
start()
# auth has to be here, so the __init__ function can be called so the dbConn var is importable from this file across all modules
import auth
import link_shortner
import politics
# we can add routes from other files using this method, the view_func being the function from the other file
app.add_url_rule('/login', view_func=auth.loginRoute,methods=["GET","POST"],)
app.add_url_rule('/signup',view_func=auth.signupRoute,methods=["GET","POST"])
app.add_url_rule('/logout',view_func=auth.logoutRoute,methods=["GET","POST"])
app.add_url_rule('/l<link_id>',view_func=link_shortner.defaultShortendLinkRoute,methods=["GET"])
app.add_url_rule('/l',view_func=link_shortner.shortendLinkHomeRoute,methods=["GET"])
app.add_url_rule('/user/politics',view_func=politics.politicsDefaultRoute,methods=["GET"])


@app.route("/")
def mainRoute():
    resp = make_response(render_template("new_main.html"), 200)
    return resp

@app.route("/new")
def newRoute():
    resp = make_response(render_template("mainpage.html"),200)
    return resp

@app.route("/", subdomain="beta",methods=["GET"])
def betaMainRoute():
    resp = make_response(render_template("mainpage.html"),200)
    return resp

@app.route("/home",methods=["GET"])
def homeRoute():
    userInfo = auth.verifySessionKeyInCookies(request)
    if userInfo == None:
        resp = make_response(redirect("/login"), 301)
    else:
        resp = make_response(render_template("home.html",username=userInfo[2]),200)
    
    return resp










if __name__ == '__main__':
    if version == "beta":
        app.config['SERVER_NAME'] = "127.0.0.1:5000"
    if version == "prod":
        app.config['SERVER_NAME'] = "callama.dev:443"
    app.run(use_reloader=True)