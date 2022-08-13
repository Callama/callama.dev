import requests
import os
import datetime


from flask import Flask, render_template, make_response, session, request, redirect


import psycopg2
from psycopg2 import IntegrityError, sql
from psycopg2.extensions import quote_ident


from global_vars import dbConn, userCache, webSessionsCache, shortendLinksCache
from cache_funcs import addOneShortLinkUsageToCache




#### FUNCTIONS ####

def addOnetoShortLinksTimesUsedInDB(link_id):
    """ 
    Add one to the times_used var of the short_links db -- DB ONLY

    :param link_id: the id of the link record to increment
    """ 
    q = f"UPDATE short_links SET times_used = times_used + 1 WHERE link_id = {link_id} "
    with dbConn.cursor() as cur:
        cur.execute(q)
        dbConn.commit()
        return True
    # when something goes wrong
    return False


#### ROUTES ####
def defaultShortendLinkRoute(link_id):
    """ 
    Only routed here when a link_id is given
    """
    try:
        shortendLink = shortendLinksCache[str(link_id)]
        print("WHAT")
        #isUpdated = addOnetoShortLinksTimesUsedInDB(link_id)
        addOneShortLinkUsageToCache(shortLinksCache, link_id)
        """ # only add to cache if it is updated in the DB
        if isUpdated == True:
            print('here')
            addOneShortLinkUsageToCache(shortLinksCache, link_id)
        else:
            # no need to worry if there really is an issue
            pass
            """
        response = make_response(redirect(shortendLink[1]),301)
        
    except KeyError:
        response = make_response('<style> body {background-color: beige;}  a:link {color: darkslateblue; text-decoration: none;} a:hover {text-decoration: none;font-size: 125%;}   </style><body><center>No Shortend Link With ID '+f"{link_id}"+' Found<br><a href="/">Home</a></center></body>',404)

    return response


def shortendLinkHomeRoute():
    return "<style> body {background-color: beige;}  a:link {color: darkslateblue; text-decoration: none;} a:hover {text-decoration: none;font-size: 125%;}   </style><body><center>Ability to create shortend links is <i>coming soon</i>.<br><a href=/home>Home</a></center></body>"