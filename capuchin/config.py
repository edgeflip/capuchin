import os

REDSHIFT_DATABASE = 'edgeflip'
REDSHIFT_HOST = 'analytics.cd5t1q8wfrkk.us-east-1.redshift.amazonaws.com'
REDSHIFT_PORT = 5439
REDSHIFT_USER = 'edgeflip'
REDSHIFT_PASSWORD = 'XzriGDp2FfVy9K'

ES_INDEX = "capuchin"
ES_HOSTS = [{"host":"localhost", "port":9200},]

TEMPLATES = "{}/capuchin/views/templates".format(os.getcwd())

MONGO_HOST = "localhost"
MONGO_PORT = 27017

RECORDS_PER_PAGE = 10

RECORD_TYPE = "user"

RECORD_FIELDS = ["fname", "lname", "age", "fbid", "city", "state"]
