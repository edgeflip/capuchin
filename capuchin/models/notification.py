import random

import humongolus as orm
from humongolus import field

from capuchin.models.client import Client, Admin
from capuchin.models.post import Post
from capuchin.models.segment import Segment


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

    def format(self):
        return self.message.format(
            Name="@[{fbid}]",
            Org=self.client.name,
        )

    @property
    def clicks(self):
        return random.randint(1000, 9999999)

    def get_post(self):
        return Post(id=self.post_id)

    def get_url(self):
        return Post.make_fb_url(self.post_id) if self.post_id else self.url

class UserNotification(Notification):

    user = field.Char()


Segment.notifications = orm.Lazy(type=Notification, key='segment')
