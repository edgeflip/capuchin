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
            "query":{
                "query_string":{
                    "default_field":"last_name.search",
                    "query":q
                }
            },
            "filter":{
                "term":{
                    "client":str(client._id)
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
        "table":"v2_user_locales",
        "key":"locales",
        "parser":basic_parser,
        "id_column":"tagged_efid",
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
        "location":parse_location,
    }

    def __init__(self, efid):
        super(UserImport, self).__init__()
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
        for t in TABLES:
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
                client_id,
                fbid
            from
                fb_app_users
                join client_app_users using (app_user_id)
            where efid = %s
        """
        self.cur.execute(query, (efid,))
        rows = self.cur.fetchall()
        self['clients'] = [
            {'asid': r['fbid'], 'id': r['client_id']}
            for r in rows
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
