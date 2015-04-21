import logging
from capuchin import config
from capuchin.models.client import Client
from capuchin.models.interest import Interest
from capuchin.models.imports import ImportOrigin
from capuchin.models import ESObject
import psycopg2
import psycopg2.extras
from flask import url_for
import random

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

    def url(self):
        return url_for('audience.view', id=self.efid)

    def get_client(self, client):
        for c in self.clients:
            if c['id'] == str(client._id): return c

        return {}


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
        city = val.split(",")[0].strip()
        state = val.split(",")[-1].strip()
    except:
        city = None
        state = None

    return {
        "location":"{}, {}".format(city, state),
        "city":city,
        "state":state
    }


def basic_parser(rows):
    return [r for r in rows]

TABLES = [
    {
        "table":"v2_user_activities",
        "key":"affiliations",
        "parser":basic_parser
    },
    {
        "table":"v2_user_likes",
        "key":"likes",
        "parser":basic_parser
    },
    {
        "table":"v2_user_languages",
        "key":"languages",
        "parser":basic_parser
    },
    {
        "table":"v2_user_permissions",
        "key":"permissions",
        "parser":basic_parser
    },
    {
        "table":"v2_users",
        "key":"self",
        "parser":None
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
        "location_name":parse_location,
    }

    def __init__(self, obj):
        super(UserImport, self).__init__()
        interests = [i.name for i in Interest.find()]
        imports = [i.name for i in ImportOrigin.find()]
        self.parse(obj)
        try:
            self.con = psycopg2.connect(
                database=config.SOURCE_DATABASE,
                port=config.SOURCE_PORT,
                user=config.SOURCE_USER,
                host=config.SOURCE_HOST,
                password=config.SOURCE_PASSWORD
            );
            self.cur = self.con.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        except Exception as e:
            logging.error(e)

        efid = self.get('efid')
        for t in TABLES:
            logging.info(efid)
            id_column = t.get("id_column", "efid")
            q = "SELECT * FROM {} WHERE {}=%s".format(t['table'], id_column)
            self.cur.execute(q, (efid,))
            rows = self.cur.fetchmany(size=100)
            if t['key'] == 'self':
                for r in rows: self.parse(r)
            else:
                self[t['key']] = t['parser'](rows)

        self.cur.execute("set schema 'magnus'")
        query = """
            select
                codename,
                fbid
            from
                fb_app_users
                join client_app_users using (app_user_id)
                join clients using (client_id)
            where efid = %s
        """
        self.cur.execute(query, (efid,))
        rows = self.cur.fetchall()
        interest = interests[random.randint(0, len(interests)-1)]
        imp = imports[random.randint(0, len(imports)-1)]
        self['interests'] = [interest]

        self['clients'] = [
            {
                'asid':row['fbid'],
                'id':str(Client.find_one({ 'slug': row['codename']})._id),
                'engagement':random.randint(1, 5),
                'import_origins': [imp],
            }
            for row in rows
        ]

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
