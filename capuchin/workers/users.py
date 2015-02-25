from celery import Celery
from celery import bootsteps
from kombu import Consumer, Exchange, Queue
from capuchin import config
from capuchin.models.user import User
from capuchin.workers import app
from capuchin.celeryconfig import efid_q
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
def test_publish():
    batch = [
        10102136605223030,
        10102136605223031,
        10102136605223032,
        10102136605223033,
        10102136605223034,
        10102136605223035,
        10102136605223036,
        10102136605223037,
    ]
    with app.producer_or_acquire(None) as producer:
        producer.publish(
            batch,
            exchange=efid_q.exchange,
            routing_key=efid_q.routing_key,
            declare=[efid_q],
            serializer='json',
        )
