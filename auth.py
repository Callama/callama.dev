import requests
import os


from flask import Flask, render_template, make_response, session, request, redirect


import psycopg2
from psycopg2 import IntegrityError, sql
from psycopg2.extensions import quote_ident
import passlib
from passlib.hash import bcrypt 

from global_vars import dbConn





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
    hashedPassword, hasher = hashPassword(password,returnHasherObj=True)

    user = matchUserInDatabase(dbConn, username)
    if user == None:
        return None

    isCorrectPassword = hasher.verify(password, hashedPassword)

    if isCorrectPassword == False:
        return False

    if isCorrectPassword == True:
        sessionKey = generateSessionKey(username, hashedPassword)

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
            username = cur.fetchone()
            dbConn.commit()
            if username == None or username == ():
                dbConn.rollback()
                return False
        except IntegrityError:
            dbConn.rollback()
            return "unique"
    return username


### Sessions ###

def generateSessionKey(username, hashedPassword):
    """ 
    Generate the session key
    Unique because each username must be unique + passwordhash for security

    :param username: str, username of user
    :param hashedPassword: str, hashed password of user

    :return: sessionKey, str, sessionKey generated from username+password
    """
    hasher = bcrypt.using(rounds=10)
    sessionKey = hasher.hash(username+hashedPassword)
    return sessionKey

### Misc Auth ###

def matchUserInDatabase(dbConn, username):
    """ 
    Find a user in the database with their username 
    To be used only for auth services

    :param dbConn: psycopg2 db object, database connection
    :param username: str, user's username 
   
    
    return None, NoneType, no user/record found

    :return: tuple, found record
    """
    print(username, "USERANEM matchUSERDB")
    cursor = dbConn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE username = %s", (username,))
    record = cursor.fetchone()
    cursor.close()
    print(record, "RECORD FROM matchUSERInDB")
    
    if record != None or record != ():
        return record
    # if no user is found, it returns () or occasionally NoneType
    if record == None or record == ():
        return None

### ROUTES ###

## Sign Ups ##

def signupRoute():
    # regular request
    if request.method == "GET":
        resp = make_response(render_template("signup.html"), 200)
        return resp
    # when submitting a request
    if request.method == "POST":
         email = request.form['email']
    password = request.form['password']
    username = request.form['username']
    
    if email == "" or password == "" or username == "":
         return redirect(f"/signup",code=302)
    user = signUpUser(dbConn, username, email, password)
    return "Account Created Succesfully!"

## LogIns ##


def loginRoute():
    # regular route
    if request.method == "GET":
        resp = make_response(render_template("login.html"), 200)
        return resp
    # when the submit button is pressed
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
    
        isVerified = verifyCredentials(dbConn, username, password)
        return f"Welcome, {isVerified}"

