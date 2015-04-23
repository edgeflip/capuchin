import random
from flask import url_for
import humongolus as orm
from humongolus import field
from capuchin import config
from capuchin.models import SearchObject, ESObject
from capuchin.models.client import Client
from capuchin.models.post import Post
from capuchin.models.segment import Segment


class Redirect(orm.EmbeddedDocument):

    original_url = field.Char()
    url = field.Char()
    path = field.Char()


class Notification(SearchObject):

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

    @property
    def clicks(self):
        return random.randint(1000, 9999999)

    def get_post(self):
        return Post(id=self.post_id)

    def get_url(self):
        return Post.make_fb_url(self.post_id) if self.post_id else self.url


class NotificationSearch(ESObject):
    TYPE = 'notification'

    @classmethod
    def filter(cls, client, q, sort):
        q = {
            "query": {
                "query_string": {
                    "default_field": "_all",
                    "query": q
                }
            },
            "filter":{
                "term":{
                    "client":str(client._id)
                }
            },
            "sort":sort
        }
        return q

    @property
    def id(self):
        return self._id

    def url(self):
        return url_for('notifications.index')


Segment.notifications = orm.Lazy(type=Notification, key='segment')
