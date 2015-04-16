from base import *
import os

try:
    env = os.getenv("ENVIRONMENT", 'dev')
    if env == 'dev': from dev import *
    if env == 'test': from test import *
    if env == 'staging': from staging import *
    if env == 'production': from production import *
    print "Imported settings for %s environment" % env
except Exception as e:
    print "ENVIRONMENT not set, using base settings."
