import psycopg2
import os
import requests


def getDBCredsandConnect(type="prod"):
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
    global dbConn
    dbConn = psycopg2.connect(**creds)
    return dbConn


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



