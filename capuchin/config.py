import os
import logging
import datetime

LOG_LEVEL = logging.INFO
DEBUG = True

SOURCE_DATABASE = 'capuchin'
SOURCE_HOST = 'edgeflip-reporting-cache.cwvoczji8mgi.us-east-1.rds.amazonaws.com'
SOURCE_PORT = 5432
SOURCE_USER = 'capuchin'
SOURCE_PASSWORD = 'Yiiphae9'

REDIRECTOR_URL = os.getenv("CHAPO_URL", "https://staging.edgeflip.com/canvas/r/")
REDIRECTOR_AUTH = os.getenv("CHAPO_AUTH", "capuchin:693828ebddb5f5b7c6f528233fca9d21b4d92941")

HASH_ROUNDS = 3998
HASH_ALGO = "pbkdf2-sha512"
HASH_ALGO_CLS = "pbkdf2_sha512"
HASH_SALT_SIZE = 32

ES_INDEX = "capuchin_v2"
ES_HOSTS = [{"host":"es", "port":9200},]

AUTH_SUBDOMAIN = "auth"

SECRET_KEY = "!!capuch1n!!"
SERVER_NAME = os.getenv("SERVER_NAME", "capuchin.dev")

SESSION_COOKIE_NAME = "capuchin"
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_DOMAIN = ".{}".format(SERVER_NAME)
SESSION_TYPE = 'mongodb'
PERMANENT_SESSION_LIFETIME = datetime.timedelta(hours=24)

REMEMBER_COOKIE_NAME = "well_hello_there"
REMEMBER_COOKIE_DURATION = datetime.timedelta(days=5)
REMEMBER_COOKIE_DOMAIN = ".{}".format(SERVER_NAME)

INFLUX_HOST = "influx"
INFLUX_PORT = 8086
INFLUX_USER = "root"
INFLUX_PASSWORD = "root"
INFLUX_DATABASE = "capuchin"

LOGGER_NAME = "capuchin"
JSON_AS_ASCII = False


TEMPLATES = "{}/capuchin/views/templates".format(os.getcwd())

MONGO_HOST = "mongo"
MONGO_PORT = 27017

RECORDS_PER_PAGE = 10
USER_RECORD_TYPE = "user"
POST_RECORD_TYPE = "post"

USER_RECORD_FIELDS = ["first_name", "last_name", "age", "efid", "location.location", "gender"]
POST_RECORD_FIELDS = ["id", "message", "picture", "link", "created_time", "from.name", "shares.count", "comments.id", "likes.id"]

FACEBOOK_APP_ID = "919803718054428"
FACEBOOK_APP_SECRET = "76bab438d5d4a14b87468ddf3a39d4da"
