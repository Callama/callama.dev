import requests
import os

from app import app, dbConn
from flask import Flask, render_template, make_response, session, request, redirect

import psycopg2
from psycopg2 import IntegrityError, sql
from psycopg2.extensions import quote_ident
import passlib
from passlib.hash import bcrypt 

from database_func import getDBCredsandConnect





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
    :return: (username, sessionKey) tuple, succesfully matched user. has user's name and sessionKey
            #TODO add any other important info from the user's record
    """
    # our flow is:
    # get password -> hash password -> find matching username + hash 
    hashedPassword, hasher = hashPassword(password,returnHasherObj=True)
    user = matchUserInDatabase(dbConn, username, hashedPassword)
    if user == None:
        return False
    isCorrectPassword = hasher.verify(password, hashedPassword)

    if isCorrectPassword == False:
        return False

    if isCorrectPassword == True:
        sessionKey = generateSessionKey(username, hashedPassword)

    userInfo = (isCorrectPassword[0],sessionKey)
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

def matchUserInDatabase(dbConn, username, hashedPassword):
    """ 
    Find a user in the database with their username and *hashed* password
    To be used only for auth services

    :param dbConn: psycopg2 db object, database connection
    :param username: str, user's username 
    :param hashedPassword: str, user's password that has been hashed with bcrypt 13 rounds
    
    return None, NoneType, no user/record found

    :return: tuple, found record
    """
    print(username, hashedPassword)
    cursor = dbConn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE username = '{username}' and password_hash = '{hashedPassword}';")
    record = cursor.fetchone()
    cursor.close()
    print(record, "RECORD FROM matchUSERInDB")
    # if no user is found, it returns () or occasionally NoneType
    if record != None or record != ():
        return record
    elif record == None or record == ():
        return None




    
    

### ROUTES ###

## Sign Ups ##

@app.route("/signup", methods=["GET"])
def signupRoute():
    resp = make_response(render_template("signup.html"), 200)
    return resp

@app.route("/signup",methods=["POST"])
def signupPostRoute():
    email = request.form['email']
    password = request.form['password']
    username = request.form['username']
    
    if email == "" or password == "" or username == "":
         return redirect(f"/signup",code=302)
    user = signUpUser(dbConn, username, email, password)
    return "Account Created Succesfully!"

## LogIns ##

@app.route("/login", methods=["GET"])
def loginRoute():
    resp = make_response(render_template("login.html"), 200)
    return resp


@app.route("/login", methods=["POST"])
def submitLoginRoute():
    username = request.form['username']
    password = request.form['password']
    
    isVerified = verifyCredentials(dbConn, username, password)
    return f"Welcome, {isVerified}"

