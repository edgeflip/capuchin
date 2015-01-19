from flask import Flask
from flask.ext.script import Manager
from flask.ext.script import Command
import psycopg2
import psycopg2.extras
import capuchin.config as config

app = Flask(__name__)

manager = Manager(app)

class SyncUsers(Command):
    "syncs users from RedShift to ElasticSearch"

    def __init__(self):
        self.con = psycopg2.connect(
            database=config.REDSHIFT_DATABASE,
            port=config.REDSHIFT_PORT,
            user=config.REDSHIFT_USER,
            host=config.REDSHIFT_HOST,
            password=config.REDSHIFT_PASSWORD);

    def run(self):
        cur = self.con.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM users u, user_aggregates ua WHERE u.fbid = ua.fbid LIMIT 1000")
        rows = cur.fetchmany(size=100)
        while rows:
            for i in rows:
                print i
            rows = cur.fetchmany(size=100)

        cur.close()
        self.con.close()

manager.add_command('sync', SyncUsers())

if __name__ == "__main__":
    manager.run()
