import psycopg2
import os
import requests




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
    


