import psycopg2

import os
import requests
from datetime import datetime



def createUserCache(dbConn):
    """ 
    Creates a user cache with the key:
    username: email, user, hashed pass

    :param dbConn: pysopg2 db conn obj, active db connection

    :return: userCache, dict, record of all users
    """
    q = "SELECT * FROM users"
    userCache = {}

    with dbConn.cursor() as cur:
        cur.execute(q)
        records = cur.fetchall()
        for user in records:
            # make the key of each record the user's name 
            key = user[2]
            userCache[key] = user
    return userCache

def addUserToCache(userCache, email, hash_password, username):
    """ 
    Add a user to the cache

    :param userCache: dict, the cache with key username: info
    :param email: str, the email of the user
    :param hash_password: str, **hashed** password of user
    :param username: str, username of the user

    :return: True, bool, succesfully added to cache
    :return: False, bool, not added to cache - error occured
    """ 
    try:
        userCache[username] = (email, hash_password, username)
        return True
    except Exception as e:
        print(f"Error Occured in adding user to Cache: {e}")
        return False

def createWebSessionsCache(dbConn):
    """ 
    Create the webSessionsCache to store web session data in a dict in the format
    {session_key: username}

    :param dbConn: pysopg2 database connection object

    :return: {session_key:username}, dict, the dict containing the session data
    """

    q = "SELECT * FROM web_sessions"
    webSessionsCache = {}

    with dbConn.cursor() as cur:
        cur.execute(q)
        records = cur.fetchall()
        for session in records:
            # make the key of each record the session key
            key = session[0]
            # the username the value of the session key
            webSessionsCache[key] = session[1]
    return webSessionsCache

def addWebSessionToCache(session_key, username, webSessionsCache):
    """
    Used when creating a new web session to be added to the cache
    
    :param session_key: str, the session key to be the key in the webSessionsCache
    :param username: str, the username to be the value of the session_key
    :param webSessionsCache: the cache to add the data to, assumed to be global_var and up-to-date
    
    :return: bool
        True, succesfully added to cache
        False, error occured, not added to cache
    """ 
    try:
        webSessionsCache[session_key] = username
        return True
    except Exception as e:
        print(e)
        return False


def removeWebsessionFromCache(session_key, webSessionsCache):
    """
    Used when removing a web session from the cache
    
    :param session_key: str, the session key to be the key in the webSessionsCache
    :param webSessionsCache: the cache to add the data to, assumed to be global_var and up-to-date
    
    :return: bool
        True, succesfully removed from cache
        False, error occured, not removed from cache
    """ 
    try:
        webSessionsCache.pop(session_key)
        return True
    except Exception as e:
        print("Error removing web session from cache", e)
        return False


#### Link Shortner ####

def populateShortendLinkCache(dbConn):
    """ 
    Populate the shortend link cache with the links in format
    {link_id : (link_id, link_address, owner_username, date_created, times_used, enabled)}

    :param dbConn: pysopg2 database connection object

    :return: dict, {link_id : (link_id, link_address, owner_username, date_created, times_used, enabled),...}
    """ 
    q = "SELECT * FROM short_links"
    shortLinksCache = {}
    with dbConn.cursor() as cur:
        cur.execute(q)
        records = cur.fetchall()
        for link in records:
            # make the key of each record the session key
            key = link[0]
            # the username the value of the session key
            shortLinksCache[key] = list(link)
    return shortLinksCache


def addShortendLinkToCache(shortLinksCache, link_id,link_address,owner_username):
    """ 
    Add a newly made shortend link with the defaults
    
    :param shortLinksCache: str, the cache to add the link to. assumed to be global
    :param link_id: str, the id of the link used in the routing link /l<link_id>
    :param link_address: str, the link to redirect to
    :param owner_username: str, the username of the short link's creator

    :return: bool
        True, succesfully added to cache
        False, error occured, not added to cache
    """ 
    try:
        shortLinksCache[link_id] = [link_id, link_address, owner_username, datetime.now().timestamp(), 0, True]
        return True
    except Exception as e:
        print("Error adding shortned link to cache:",e)
        return False

def addOneShortLinkUsageToCache(shortLinksCache, link_id):
    """ 
    Increments the times_used value in the cache by one
    :param shortLinksCache: str, the cache to add the link to. assumed to be global
    :param link_id: str, the id of the link used in the routing link /l<link_id>
    """ 
    shortLinksCache[link_id][4] += 1
    print(shortLinksCache[link_id])
    



