import requests
import os
from boto.s3.connection import S3Connection



def verifyCredentials(session, email, password):
    ...


def getDBCredsandConnect(session,type="beta"):
    # when it is being ran on an enviroment that is not heroku
    if type == "beta":
        api_key = os.environ['heroku_api_key']

    if type == "prod":
       api_key = os.environ['api_key']

    req = requests.get("https://api.heroku.com/apps/callamadev/config-vars",headers={"Authorization": f"Bearer {api_key}", "Accept": "application/vnd.heroku+json; version=3"})
    creds = req.json()
    # remove this from the data 
    creds.pop("api_key")
   


