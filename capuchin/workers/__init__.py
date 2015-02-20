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
        last = client.last_insights
        if not last:
            last = datetime.datetime.utcnow() - datetime.timedelta(days=90)
        logging.info("Last Insights for {}: {}".format(client.name, last))
        i = Insights(client=client, id=client.facebook_page.id, since=last)
        client.last_insights = datetime.datetime.utcnow()
        client.save()

@app.task
def get_feeds():
    for client in Client.find():
        last = client.last_post
        logging.info("Last Posts for {}: {}".format(client.name, last))
        i = ClientPosts(client=client, since=last)
        client.last_post = datetime.datetime.utcnow()
        client.save()

get_insights()
get_feeds()
