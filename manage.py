from flask import Flask
from flask.ext.script import Manager
from flask.ext.script import Command
import psycopg2
import psycopg2.extras
import capuchin.config as config
from capuchin.app import Capuchin
from capuchin.models.user import User
from pprint import pprint

app = Capuchin()
manager = Manager(app)

TOTAL = 10000

class SyncUsers(Command):
    "syncs users from RedShift to ElasticSearch"

    def get_rows(self, offset=0, limit=1000):
        offset = 0
        limit = 1000
        def execute():
            self.cur.execute("SELECT * FROM users u, user_aggregates ua WHERE ua.fbid = u.fbid LIMIT %s OFFSET %s", (limit, offset))
            rows = self.cur.fetchmany(size=100)
            while rows:
                for i in rows:
                    yield i
                rows = self.cur.fetchmany(size=100)

        while offset < TOTAL:
            yield execute()
            offset+=limit



    def __init__(self):
        self.con = psycopg2.connect(
            database=config.REDSHIFT_DATABASE,
            port=config.REDSHIFT_PORT,
            user=config.REDSHIFT_USER,
            host=config.REDSHIFT_HOST,
            password=config.REDSHIFT_PASSWORD);

        self.cur = self.con.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    def run(self):
        for i in self.get_rows():
            for row in i:
                u = User(row)
                pprint(u)
                app.es.index(index=config.ES_INDEX, doc_type="user", body=u)

        self.cur.close()
        self.con.close()

manager.add_command('sync', SyncUsers())

if __name__ == "__main__":
    manager.run()
