import requests
import os


from flask import Flask, render_template, make_response, session, request, redirect


import psycopg2
from psycopg2 import IntegrityError, sql
from psycopg2.extensions import quote_ident
import passlib
from passlib.hash import bcrypt 

from global_vars import dbConn, userCache, webSessionsCache
from cache_funcs import addUserToCache, addWebSessionToCache, removeWebsessionFromCache





### passwords ###

def hashPassword(password,returnHasherObj=False):
    """ 
    Hashes any given password

    :param password: str, the password to hash
    :param returnHasherObj: bool, wheater to return the "hasher" object or not
        default False

    :return: hash, str, the password hashed
    :return: hasher, bycrpt.using object, returned in "returnHasherObj" is True
    """
    # establish the hasher
    hasher = bcrypt.using(rounds=13)
    # hash the password
    hash = hasher.hash(password)
    if returnHasherObj == True:
        return hash, hasher
    return hash

def verifyCredentials(dbConn, username, password):
    """ 
    Verifies a user's credentials when given a username + password

    :param dbConn: pysopg2 DB conn. obj
    :param username: str, the username of the user
    :param password: str, the non-hashed version of the user's password

    :return: False, bool, no user found with matching username AND password
    :return: None, NoneType, no user found at all.
    :return: (username, sessionKey) tuple, succesfully matched user. has user's name and sessionKey
            #TODO add any other important info from the user's record
    """
    # our flow is:
    # get password -> find matching username -> get their hash -> match hash to password -> make session
   

    user = matchUserInDatabase(dbConn, username)
    if user == None:
        return None
    # user[1] is the hashed password we got when the user signed up
    hasher = bcrypt.using(rounds=13)
    isCorrectPassword = hasher.verify(password, user[1])

    if isCorrectPassword == False:
        return False

    if isCorrectPassword == True:
        sessionKey = generateSessionKey(username, user[1])

    userInfo = (username, sessionKey)
    return userInfo

### Sign-Ups ###


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
    q = f"INSERT INTO users(email, password_hash, username) VALUES(%s, %s, %s) RETURNING username, email, password_hash;"

    with dbConn.cursor() as cur:
        try:
            cur.execute(q,(email, hashedPassword, username,))
            userInfo = cur.fetchone()
            dbConn.commit()

            if userInfo == None or userInfo == ():
                dbConn.rollback()
                return False

            # once this happens, we're safe to add it to the cache
            addedToCache = addUserToCache(userCache, email, hashedPassword, username)
            print(addedToCache)
            print(userCache)
            
        except IntegrityError:
            dbConn.rollback()
            return "unique"
        sessionKey = generateSessionKey(username, password)
    return sessionKey


### Sessions ###

def generateSessionKey(username, password):
    """ 
    Generate the session key
    Unique because each username must be unique + password

    :param username: str, username of user
    :param password: str, password of user 

    :return: sessionKey, str, sessionKey generated from username+password
    """
    hasher = bcrypt.using(rounds=10)
    sessionKey = hasher.hash(username+password)
    return sessionKey


def addSessionKeyToDB(sessionKey, username):
    """
    Add a session key to the database, and just the DB

    :param username: str, username of user
    :param sessionKey: str, sessionKey from generateSessionKey function

    :return: bool
        True, success
        False, failed
    """
    q = f"INSERT INTO web_sessions(session_key, username) VALUES(%s,%s)"
    with dbConn.cursor() as cur:
            cur.execute(q,(sessionKey, username,))
            dbConn.commit()
            return True
    # some error occurs
    dbConn.rollback()
    print("Error in adding web_session to database")
    return False

def createWebSession(session_key, username):
    """
    Add a web session to the databse AND cache

    :param username: str, username of user
    :param sessionKey: str, sessionKey from generateSessionKey function

    :return: bool
        True, success
        False, failed
    """
    isAddedToDB = addSessionKeyToDB(session_key, username)
    if isAddedToDB == False:
        return False
    # add to cache
    isAddedToCache = addWebSessionToCache(session_key, username, webSessionsCache)
    if isAddedToCache == False:
        # if it's not in the cache, we don't want it in the DB and to cause issues
        removeWebSessionFromDB(session_key)
    return True

def removeWebSessionFromDB(session_key):
    """ 
    Delete a web_session with the session_key

    :param session_key: the session_key which we will be deleting

    :return: bool
        True, success
        False, failed
    """
    
    q = "DELETE FROM web_sessions WHERE session_key = %s"
    with dbConn.cursor() as cur:
        cur.execute(q,(session_key,))
        dbConn.commit()
        return True
    
    print("Error in deleting web_session from DB")
    return False
            
def verifySessionKeyInCookies(request):
    """
    Check to see if the 'session' cookie is valid and has an account logged in w/ it

    :return: None, NoneType, when no cookie or user is found
    :return: (email, user, passwordhash), tuple, the userinfo of the user's data
    """ 

    session_key = request.cookies.get('session')
    if session_key == None:
        return None
    # check to see if the session has an account linked
    try:
        username = webSessionsCache[session_key]
    except KeyError:
        return None
    userInfo = userCache[username]
    return userInfo
    


    


### Misc Auth ###

def matchUserInDatabase(dbConn, username,usingCache=True):
    """ 
    Find a user in the database with their username 
    To be used only for auth services

    :param dbConn: psycopg2 db object, database connection
    :param username: str, user's username 
    :param usingCache: bool, wheather to use the userCache or not
        default: True
    
    return None, NoneType, no user/record found

    :return: tuple, found record
    """
    if usingCache == False:
        cursor = dbConn.cursor()
        cursor.execute(f"SELECT * FROM users WHERE username = %s", (username,))
        record = cursor.fetchone()
        cursor.close()

        # this only applies to this method, so we have it here
        if record == None or record == ():
            return None

    if usingCache == True:
        try:
            record = userCache[username]
        except KeyError:
            return None
    
    if record != None or record != ():
        return record
    
    

### ROUTES ###

## Sign Ups ##

def signupRoute():
    # regular request
    if request.method == "GET":
        resp = make_response(render_template("signup.html",messageValue="Sign Up"),200)
        return resp
    # when submitting a request
    if request.method == "POST":
         email = request.form['email']
    password = request.form['password']
    username = request.form['username']
    # this removes any extra spaces
    username.strip()
    password.strip()

    if email == "" or password == "" or username == "":
        return make_response(render_template("signup.html", messageValue="All fields are required."), 400)
    user = signUpUser(dbConn, username, email, password)
    if user == False:
        return make_response(render_template(f"signup.html",messageValue="An error has occured."), 400)
    if user == "unique":
        return make_response(render_template(f"signup.html",messageValue="That username has already been taken."), 400)
    else:
        sessionKey = generateSessionKey(username, password)
        response = make_response(redirect("/home"),301)
        response.set_cookie("session", sessionKey)
        isSessionCreated = createWebSession(sessionKey, username)
    return response
## LogIns ##


def loginRoute():

    # regular route
    if request.method == "GET":
        # we check if they're already logged in
        userInfo = verifySessionKeyInCookies(request)
        print(userInfo)
        if userInfo == None:
            resp = make_response(render_template("login.html",messageValue="Login Below"), 200)
        else:
            resp = make_response(redirect("/home"),301)
       
        return resp
    # when the submit button is pressed
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        # this removes any extra spaces
        username.strip()
        password.strip()
        
        isVerified = verifyCredentials(dbConn, username, password)

        # when the user used invalid credentials
        if isVerified == False or isVerified == None:
            resp = make_response(render_template("login.html",messageValue="Incorrect Username or Password"), 200)
            return resp

        # make the session cookie, add it to cache + database for conttinuity
        sessionKey = generateSessionKey(username, password)
        response = make_response(redirect("/home"), 301)
        response.set_cookie("session", sessionKey)
        isSessionCreated = createWebSession(sessionKey, username)

        return response

def logoutRoute():
    session_key = request.cookies.get("session")
    resp = make_response(redirect("/"),301)
    resp.delete_cookie('session')
    removeWebSessionFromDB(session_key)
    removeWebsessionFromCache(session_key, webSessionsCache)
    return resp
    
