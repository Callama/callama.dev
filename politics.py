import requests
import os
import datetime


from flask import Flask, render_template, make_response, session, request, redirect


import psycopg2
from psycopg2 import IntegrityError, sql
from psycopg2.extensions import quote_ident


from global_vars import dbConn, userCache, webSessionsCache

def politicsDefaultRoute():
    return "<style> body {background-color: beige;}  a:link {color: darkslateblue; text-decoration: none;} a:hover {text-decoration: none;font-size: 125%;}   </style><body><center>Politics is <i>coming soon</i>.<br><a href=/home>Home</a></center></body>"