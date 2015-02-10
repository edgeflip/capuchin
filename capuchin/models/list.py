from flask import url_for
import humongolus as orm
import humongolus.field as field
from capuchin.app import ES
from capuchin import config
from capuchin.models.client import Client

class List(orm.Document):
    _db = "capuchin"
    _collection = "lists"
    _indexes = [
        orm.Index('client', key=('client', 1), unique=True),
    ]
    name = field.Char()
    auth_url = field.Char()
    thanks_url = field.Char()
    client = field.DocumentId(type=Client)

    @property
    def url(self):
        return url_for("redirect.list", id=str(self._id), _external=True)

    @property
    def users(self):
        res = ES.count(
            config.ES_INDEX,
            config.RECORD_TYPE
        )

        return res['count']

Client.lists = orm.Lazy(type=List, key='client')
