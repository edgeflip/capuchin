from flask import Flask
from flask.ext.script import Manager
from flask.ext.script import Command
import psycopg2
import psycopg2.extras
import capuchin.config as config
from capuchin import Capuchin
from capuchin.models.user import User
from capuchin.models.client import Client
from capuchin.workers.client_insights import ClientInsights
from capuchin import user_mapping
from capuchin import ES
import logging

app = Capuchin()
manager = Manager(app)

TOTAL = 1000000

class RunWorker(Command):

    def run(self):
        for client in Client.find():
            logging.info(client.name)
            i = ClientInsights(client=client)

class SyncUsers(Command):
    "syncs users from RedShift to ElasticSearch"

    def get_rows(self, offset=0, limit=1000):
        def execute():
            self.cur.execute("SELECT * FROM v2_users u LIMIT %s OFFSET %s", (limit, offset))
            rows = self.cur.fetchmany(size=100)
            while rows:
                for i in rows:
                    yield i
                rows = self.cur.fetchmany(size=100)

        while offset < TOTAL:
            yield execute()
            offset+=limit



    def __init__(self):
        try:
            self.con = psycopg2.connect(
                database=config.REDSHIFT_DATABASE,
                port=config.REDSHIFT_PORT,
                user=config.REDSHIFT_USER,
                host=config.REDSHIFT_HOST,
                password=config.REDSHIFT_PASSWORD);

            self.cur = self.con.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        except: pass

    def run(self):
        #offset = ES.count(config.ES_INDEX, config.RECORD_TYPE)['count']
        #logging.info(offset)
        for i in self.get_rows(offset=0):
            for row in i:
                u = User(row)
                logging.info(u)
                ES.index(index=config.ES_INDEX, doc_type=config.RECORD_TYPE, body=u)

        self.cur.close()
        self.con.close()

class UpdateMapping(Command):

    def run(self):
        ES.indices.put_mapping(index=config.ES_INDEX, doc_type=config.RECORD_TYPE, body=user_mapping.USER)

manager.add_command('sync', SyncUsers())
manager.add_command('update', UpdateMapping())
manager.add_command('insights', RunWorker())

if __name__ == "__main__":
    manager.run()
