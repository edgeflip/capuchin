import humongolus as orm
import humongolus.field as field
from capuchin.models.segment import Segment
from capuchin.models.user import User
from capuchin.models.post import Post
from capuchin.models.client import Client
from capuchin.models.event import Event
from capuchin import config
from flask_oauth import OAuth
import requests
import logging
import math
import random
import datetime

class Redirect(orm.EmbeddedDocument):
    original_url = field.Char()
    url = field.Char()
    path = field.Char()

class Notification(orm.Document):
    _db = "capuchin"
    _collection = "notifications"
    _indexes = [
        orm.Index('segment', key=('segment', 1)),
        orm.Index('clients', key=('client', 1)),
        orm.Index('post_id', key=('post_id', 1)),
    ]

    message = field.Char()
    segment = field.ModelChoice(type=Segment)
    client = field.DocumentId(type=Client)
    post_id = field.Char()
    url = field.Char()
    redirect = Redirect()
    smart = field.Boolean(default=False)

    def get_post(self):
        return Post(id=self.post_id)

    def send(self):
        send_notifications.delay(str(self._id))

    def get_url(self):
        if self.post_id:
            p = self.get_post()
            return "https://facebook.com/{}".format(p.id)
        else:
            return self.url

    @property
    def clicks(self):
        return random.randint(1000, 9999999)

    def post(self, user):
        asid = "10153577819234377"#ASID for Chris Cote for CapuchinDev app, should be None
        #for i in user.get('clients', []):
        #    if str(i.get('id')) == str(self.client._id):
        #        asid = i.get('asid')
        if asid:
            """res = requests.post(
                "https://graph.facebook.com/{}/notifications".format(asid),
                data={
                    "access_token":"{}|{}".format(config.FACEBOOK_APP_ID, config.FACEBOOK_APP_SECRET),
                    "template":self.message,
                    "href":"/test?key=12345",
                    "ref":"test",
                }
            )
            j = res.json()
            """
            j = {'success':True}
            logging.info("Notification:{}".format(j))
            event_type = "notification_sent" if j.get("success") else "notification_failure"
            user.last_notification = datetime.datetime.utcnow()
            User.save(data=user)
            Event(self.client, event_type, value=1, user=asid, notification=str(self._id))

Segment.notifications = orm.Lazy(type=Notification, key='segment')
