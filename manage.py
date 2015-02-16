from flask import Flask
from flask.ext.script import Manager
from flask.ext.script import Command
import psycopg2
import psycopg2.extras
import capuchin.config as config
from capuchin.app import Capuchin
from capuchin.models.user import User
from capuchin.models.client import Client
from capuchin.models.city import City
from capuchin.workers.client.insights import Insights
from capuchin.workers.client.posts import ClientPosts
from capuchin import user_mapping
from capuchin import db
import csv
import datetime
import logging

app = Capuchin()
manager = Manager(app)

TOTAL = 1000000

class PageInsights(Command):

    def run(self):
        for client in Client.find():
            logging.info(client.name)
            last = client.last_insights
            if not last:
                last = datetime.datetime.utcnow() - datetime.timedelta(days=90)
            i = Insights(client=client, id=client.facebook_page.id, since=last)
            client.last_insights = datetime.datetime.utcnow()
            client.save()

class PageFeed(Command):

    def run(self):
        for client in Client.find():
            last = client.last_post
            i = ClientPosts(client=client, since=last)
            client.last_post = datetime.datetime.utcnow()
            client.save()

class SyncUsers(Command):
    "syncs users from RedShift to ElasticSearch"
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

    def run(self):
        ES = db.init_elasticsearch()
        offset = ES.count(config.ES_INDEX, config.USER_RECORD_TYPE)['count']
        logging.info(offset)
        for i in self.get_rows(offset=offset):
            for row in i:
                logging.info(row)
                u = User(row)
                logging.info(u)
                ES.index(index=config.ES_INDEX, doc_type=config.USER_RECORD_TYPE, body=u, id=u['efid'])

        self.cur.close()
        self.con.close()

class UpdateMapping(Command):

    def run(self):
        ES = db.init_elasticsearch()
        db.create_index(ES)
        ES.indices.put_mapping(index=config.ES_INDEX, doc_type=config.USER_RECORD_TYPE, body=user_mapping.USER, ignore_conflicts=True)

class LoadCities(Command):

    def run(self):
        with open("./data/states_abbreviations.csv") as states:
            rows = csv.DictReader(states, delimiter=",")
            abbrvs = {r['Abbreviation']:r['State'] for r in rows}
        with open("./data/cities.csv") as cities:
            rows = csv.DictReader(cities, delimiter=",")
            for r in rows:
                r['full_state'] = abbrvs[r['state']]
                c = City(data=r)
                logging.info(c.json())
                try:
                    c.save()
                except Exception as e:
                    logging.exception(e)


manager.add_command('sync', SyncUsers())
manager.add_command('update', UpdateMapping())
manager.add_command('insights', PageInsights())
manager.add_command('feeds', PageFeed())
manager.add_command('load_cities', LoadCities())

if __name__ == "__main__":
    manager.run()
