from celery import Celery
from capuchin import config
from capuchin.models.client import Client, Competitor
from capuchin import db
from capuchin.workers.client.insights import Insights
from capuchin.workers.client.posts import ClientPosts
from capuchin.workers.client.competitors import Competitors
import humongolus
import logging
import datetime

app = Celery(__name__)
app.config_from_object('capuchin.celeryconfig')
humongolus.settings(logging, db.init_mongodb())

@app.task
def client_insights(client):
    if not isinstance(client, Client): client = Client(id=client)
    last = client.social.facebook.last_sync
    if not last:
        last = datetime.datetime.utcnow() - datetime.timedelta(days=90)
    logging.info("Last Insights for {}: {}".format(client.name, last))
    Insights(client=client, id=client.social.facebook.id, since=last)
    client.social.facebook.last_sync = datetime.datetime.utcnow()
    client.save()
    logging.info("Saved client")

@app.task
def get_insights():
    for client in Client.find():
        try:
            client_insights(client)
        except Exception as e:
            logging.error(e)


@app.task
def spy_on_competitors():
    for client in Client.find():
        try:
            competitors = Competitors(client)
            competitors.spy_on_competitors()
        except Exception as e:
            logging.error(e)

@app.task
def client_feed(client):
    if not isinstance(client, Client): client = Client(id=client)
    last = client.last_post
    logging.info("Last Posts for {}: {}".format(client.name, last))
    ClientPosts(client=client, since=last)
    client.last_post = datetime.datetime.utcnow()
    client.save()

@app.task
def get_feeds():
    for client in Client.find():
        try:
            client_feed(client)
        except Exception as e:
            logging.error(e)

#get_insights()
#get_feeds()
#spy_on_competitors()
