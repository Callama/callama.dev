import psycopg2


def fetchOne(dbConn, query):
    # if we have an cleaned argument in the query, in a seperate part, we want to remove the set of () holding the two parts together
    if len(query) > 1:
        query = query[0]
        
    cursor = dbConn.cursor()
    cursor.execute(query)
    record = cursor.fetchone()
    cursor.close()

    return record

