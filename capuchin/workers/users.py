from celery import bootsteps
from kombu import Consumer
from capuchin import config
from capuchin import db
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
        ES = db.init_elasticsearch()
        for efid in data:
            logging.info("Processing EFID: {}".format(efid))
            new_user = User(efid)
            logging.info("Successfully read User: {}".format(new_user))
            ES.index(index=config.ES_INDEX, doc_type=config.USER_RECORD_TYPE, body=new_user, id=efid)
            logging.info("Successfully indexed")
        message.ack()

app.steps['consumer'].add(BatchEFID)

@app.task
def test_publish():
    batch = [
        10102136605223030,
    ]
    with app.producer_or_acquire(None) as producer:
        producer.publish(
            batch,
            exchange=efid_q.exchange,
            routing_key=efid_q.routing_key,
            declare=[efid_q],
            serializer='json',
        )
