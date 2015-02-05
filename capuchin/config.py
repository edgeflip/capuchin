import os
import logging
import datetime

LOG_LEVEL = logging.INFO
DEBUG = True


REDSHIFT_DATABASE = 'edgeflip'
REDSHIFT_HOST = 'analytics.cd5t1q8wfrkk.us-east-1.redshift.amazonaws.com'
REDSHIFT_PORT = 5439
REDSHIFT_USER = 'edgeflip'
REDSHIFT_PASSWORD = 'XzriGDp2FfVy9K'

ES_INDEX = "capuchin"
ES_HOSTS = [{"host":"es", "port":9200},]

AUTH_SUBDOMAIN = "auth"

SECRET_KEY = "!!capuch1n!!"
SERVER_NAME = "capuchin.dev"

SESSION_COOKIE_NAME = "capuchin"
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_DOMAIN = ".{}".format(SERVER_NAME)
SESSION_TYPE = 'mongodb'
PERMANENT_SESSION_LIFETIME = datetime.timedelta(hours=24)

REMEMBER_COOKIE_NAME = "well_hello_there"
REMEMBER_COOKIE_DURATION = datetime.timedelta(days=5)
REMEMBER_COOKIE_DOMAIN = ".{}".format(SERVER_NAME)

LOGGER_NAME = "capuchin"
JSON_AS_ASCII = False


TEMPLATES = "{}/capuchin/views/templates".format(os.getcwd())

MONGO_HOST = "mongo"
MONGO_PORT = 27017

RECORDS_PER_PAGE = 10

RECORD_TYPE = "user"

RECORD_FIELDS = ["fname", "lname", "age", "fbid", "city", "state"]

FACEBOOK_APP_ID = "341894559353627"
FACEBOOK_APP_SECRET = "c1107e87bddcc6902eb692a528fd43d5"
