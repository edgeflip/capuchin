import json
import ast
import logging
from capuchin import config
from capuchin.models.client import Client
from capuchin.models import ESObject
import psycopg2
import psycopg2.extras

class User(ESObject):
    TYPE = config.USER_RECORD_TYPE

    @classmethod
    def filter(cls, client, q, sort):
        q = {
            "filter":{
                "term":{
                    "clients.id":str(client._id)
                }
            },
            "sort":sort
        }
        return q


def parse_email(val):
    try:
        handle = val.split("@")[0]
        domain = val.split("@")[-1]
    except:
        handle = None
        domain = None
    return {
        "email":val,
        "handle":handle,
        "domain":domain
    }

def parse_location(val):
    try:
        city = val.split(", ")[0]
        state = val.split(", ")[-1]
    except:
        city = None
        state = None

    return {
        "location":val,
        "city":city,
        "state":state
    }

def affiliations(rows):
    return [r for r in rows]

def likes(rows):
    return [r for r in rows]

def top_words(rows):
    return [r.get("word") for r in rows]


TABLES = [
    {
        "table":"v2_activities",
        "key":"affiliations",
        "parser":affiliations
    },
    {
        "table":"v2_page_likes",
        "key":"likes",
        "parser":likes
    },
    {
        "table":"v2_top_words",
        "key":"top_words",
        "parser":top_words
    },
    {
        "table":"v2_user_aggregates",
        "key":"self",
        "parser":None
    }
]

class UserImport(dict):

    key_parsers = {
        "email":parse_email,
        "location":parse_location,
    }

    def __init__(self, obj):
        super(UserImport, self).__init__()
        self.parse(obj)
        try:
            self.con = psycopg2.connect(
                database=config.REDSHIFT_DATABASE,
                port=config.REDSHIFT_PORT,
                user=config.REDSHIFT_USER,
                host=config.REDSHIFT_HOST,
                password=config.REDSHIFT_PASSWORD
            );
            self.cur = self.con.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        except Exception as e:
            logging.error(e)
        for t in TABLES:
            q = "SELECT * FROM {} WHERE efid=%s".format(t['table'])
            self.cur.execute(q, (obj.get("efid"),))
            rows = self.cur.fetchmany(size=100)
            if t['key'] == 'self':
                for r in rows: self.parse(r)
            else:
                self[t['key']] = t['parser'](rows)

        self['clients'] = [{'asid':self['efid'], 'id':str(c._id)} for c in Client.find()]

    def parse(self, obj):
        for k,v in obj.iteritems():
            if k in self.key_parsers:
                try:
                    v = self.key_parsers[k](v)
                except Exception as e:
                    logging.error(e)
                    pass

            v = None if not v else v
            self[k] = v
