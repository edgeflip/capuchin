from flask import Flask
from flask.ext.script import Manager
from flask.ext.script import Command
import psycopg2
import psycopg2.extras
import capuchin.config as config
from capuchin.models.user import UserImport
from capuchin.app import Capuchin
from capuchin.models.client import Client
from capuchin.models.interest import Interest
from capuchin.models.city import City
from capuchin.workers.client.insights import Insights
from capuchin.workers.client.posts import ClientPosts
from capuchin import user_mapping
from capuchin import db
from gevent import monkey
import gevent
import math
import csv
import datetime
import logging

monkey.patch_all()

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

    def get_cursor(self):
        con = psycopg2.connect(
            database=config.SOURCE_DATABASE,
            port=config.SOURCE_PORT,
            user=config.SOURCE_USER,
            host=config.SOURCE_HOST,
            password=config.SOURCE_PASSWORD);

        cur = con.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        return cur

    def get_total(self):
        cur = self.get_cursor()
        cur.execute("SELECT COUNT(*) FROM v2_users")
        count = cur.fetchmany()
        return count[0]['count']

    def worker(self, offset, total):
        limit = 1000
        rows_loaded = 0
        cur = self.get_cursor()
        ES = db.init_elasticsearch()

        def execute():
            cur.execute("SELECT * FROM v2_users u LIMIT %s OFFSET %s", (limit, offset))
            rows = cur.fetchmany(size=100)
            while rows:
                for row in rows:
                    logging.info(row)
                    u = UserImport(row)
                    logging.info(u)
                    ES.index(index=config.ES_INDEX, doc_type=config.USER_RECORD_TYPE, body=u, id=u['efid'])
                rows = cur.fetchmany(size=100)

        while rows_loaded < total:
            logging.info("ROWS LOADED: {}".format(rows_loaded))
            execute()
            offset+=limit
            rows_loaded+=limit

        cur.close()

    def run(self):
        ES = db.init_elasticsearch()
        offset = ES.count(config.ES_INDEX, config.USER_RECORD_TYPE)['count']
        diff = self.get_total() - offset
        logging.info("DIFF: {}".format(diff))
        worker_total = math.ceil(diff/10) if diff > 10 else diff
        gs = []
        r = range(10) if diff > 10 else range(1)
        for i in range(10):
            gs.append(gevent.spawn(self.worker, offset=offset, total=worker_total))

        gevent.joinall(gs)

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

class LoadInterests(Command):

    def run(self):
        with open("./data/interests.txt") as interests:
            for l in interests:
                i = Interest(data={'name':l.strip()})
                i.save()

class InitApp(Command):

    def  run(self):
        es = db.init_elasticsearch()
        db.create_index(es)
        influx = db.init_influxdb()
        db.create_shards(influx)

manager.add_command('sync', SyncUsers())
manager.add_command('update', UpdateMapping())
manager.add_command('insights', PageInsights())
manager.add_command('feeds', PageFeed())
manager.add_command('load_cities', LoadCities())
manager.add_command('load_interests', LoadInterests())
manager.add_command('init', InitApp())

if __name__ == "__main__":
    manager.run()
