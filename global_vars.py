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


def __init__():
    global version
    version="prod"

    global dbConn
    dbConn = getDBCredsandConnect(type=version)
    print("Created Global Var. for DB connection in global_vars.py")
    return dbConn