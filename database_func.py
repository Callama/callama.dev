import psycopg2



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
    global dbConn
    dbConn = psycopg2.connect(**creds)
    return dbConn
    
def fetchOne(dbConn, query):
    # if we have an cleaned argument in the query, in a seperate part, we want to remove the set of () holding the two parts together
    if len(query) > 1:
        query = query[0]
        
    cursor = dbConn.cursor()
    cursor.execute(query)
    record = cursor.fetchone()
    cursor.close()

    return record

