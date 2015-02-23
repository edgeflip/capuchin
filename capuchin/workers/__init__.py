from celery import Celery
from capuchin import config
from capuchin.app import Capuchin
from capuchin.models.client import Client
from capuchin.workers.client.insights import Insights
from capuchin.workers.client.posts import ClientPosts
import logging
import datetime

init = Capuchin()

app = Celery(__name__)
app.config_from_object('capuchin.celeryconfig')

@app.task
def get_insights():
    for client in Client.find():
        try:
            last = client.social.facebook.last_sync
            if not last:
                last = datetime.datetime.utcnow() - datetime.timedelta(days=90)
            logging.info("Last Insights for {}: {}".format(client.name, last))
            i = Insights(client=client, id=client.social.facebook.id, since=last)
            client.social.facebook.last_sync = datetime.datetime.utcnow()
            client.save()
        except Exception as e:
            logging.error(e)

@app.task
def get_feeds():
    for client in Client.find():
        try:
            last = client.last_post
            logging.info("Last Posts for {}: {}".format(client.name, last))
            i = ClientPosts(client=client, since=last)
            client.last_post = datetime.datetime.utcnow()
            client.save()
        except Exception as e:
            logging.error(e)

get_insights()
get_feeds()
