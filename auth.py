import requests
import os

from app import app, dbConn
from flask import Flask, render_template, make_response, session, request, redirect

import psycopg2
from psycopg2 import IntegrityError
import passlib
from passlib.hash import bcrypt 

from database_func import fetchOne


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


### passwords ###

def hashPassword(password):
    # establish the hasher
    hasher = bcrypt.using(rounds=13)
    # hash the password
    hash = hasher.hash(password)
    return hash


def matchUserInDatabase(dbConn, username, hashedPassword):
    record = fetchOne(dbConn, (f"SELECT * FROM users WHERE username = %s and password_hash = {hashedPassword}", (username,)))
    if record != None or record != ():
        return record
    elif record == None or record == ():
        return None


def signUpUser(dbConn, username, email, password):
    """ 

    Add a user to the database when given a unique username and email
    And a password that will be added to the DB in a *hashed* format
    
    :param dbConn: pysopg2 db object, database connection
    :param username: str, user's username on signup
    :param email: str, user's email on signup
    :param password: str, user's password on signup

    :return: "unique" str, user's email or password has already been used
    :return: False bool, unkown error occured
    :return: sessionKey str, succesfully signed up user, session key to be put in cookie jar of browser 

    """
    # flow:
    # get email + user + password -> hash password -> store in database 
    hashedPassword = hashPassword(password)
    q = f"INSERT INTO users(email, password_hash, username) VALUES(%s, %s, %s) RETURNING username;"
    with dbConn.cursor() as cur:
        try:
            cur.execute(q,(email, hashedPassword, username,))
            username = cur.fetchone()
            dbConn.commit()
            if username == None or username == ():
                return False
        except IntegrityError:
            return "unique"
    return username



def generateSessionKey(username):
    """ 
    Generate the session key
    Unique because each username must be unique

    :param username: str, username of user

    :return: sessionKey, str, sessionKey generated from username
    """
    hasher = bcrypt.using(rounds=10)
    sessionKey = hasher.hash(username)
    return sessionKey


def verifyCredentials(dbConn, session, username, password):
    # our flow is:
    # get password -> hash password -> find matching username + hash 
    hashedPassword = hashPassword(password)
    user = matchUserInDatabase(dbConn, username, hashedPassword)
    if user == None:
        return False
    





   

### ROUTES ###

@app.route("/signup", methods=["GET"])
def signupRoute():
    resp = make_response(render_template("signup.html"), 200)
    return resp

@app.route("/signup",methods=["POST"])
def signupPostRoute():
    email = request.form['email']
    password = request.form['password']
    username = request.form['username']
    user = signUpUser(dbConn, username, email, password)
    return user
    
  
