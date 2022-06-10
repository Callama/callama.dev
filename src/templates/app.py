from flask import Flask, render_template, make_response, session, request, redirect
import psycopg2

import os
import json



# in the Procfile, we have app:app. this is looking for the file, app, with the webserver var, app. it must match.
app = Flask(__name__,template_folder="templates")
app.config["DEBUG"] = True

@app.route("/")
def mainRoute():
    resp = make_response(render_template("helloworld.html"), 200)
    return resp





if __name__ == '__main__':
    app.run()