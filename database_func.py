import psycopg2
import os
import requests




def createUserCache(dbConn):
    """ 
    Creates a user cache with the key:
    (username, hashed password): email, user, hashed pass

    :param dbConn: pysopg2 db conn obj, active db connection

    :return: userCache, dict, record of all users
    """
    q = "SELECT * FROM users"
    userCache = {}

    with dbConn.cursor() as cur:
        cur.execute(q)
        records = cur.fetchall()
        for user in records:
            # make the key of each record the user's name and hashed password for quick lookup
            key = (user[2], user[1])
            userCache[key] = user
    return userCache



