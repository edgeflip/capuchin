from celery import Celery
from celery import bootsteps
from kombu import Consumer, Exchange, Queue
from capuchin import config
from capuchin import db
from capuchin.models.user import User
from capuchin.models.client import Client
from capuchin.workers import app
from capuchin.celeryconfig import efid_q
import time
import datetime
import logging

class BatchEFID(bootsteps.ConsumerStep):

    def get_consumers(self, channel):
        return [Consumer(channel,
                         queues=[efid_q],
                         callbacks=[self.handle_message],
                         accept=['json'])]

    def handle_message(self, data, message):
        logging.info(data)
        for id in data:
            logging.info("Processing EFID: {}".format(id))

        message.ack()


app.steps['consumer'].add(BatchEFID)

@app.task
def members_lifetime():
    INFLUX = db.init_influxdb()
    for c in Client.find():
        try:
            count = User.count(client=c)
            points = [[
                time.mktime(datetime.datetime.utcnow().timetuple()),
                count,
                "members.lifetime",
            ]]
            logging.info("Members Lifetime: {} = {}".format(c.name, count))
            db.write_influx(INFLUX, c, points, "members.lifetime", prefix="insights")
        except Exception as e:
            logging.error(e)


members_lifetime()
