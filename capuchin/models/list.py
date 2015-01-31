from flask import url_for
import humongolus as orm
import humongolus.field as field
from capuchin import ES
from capuchin import config

class List(orm.Document):
    _db = "capuchin"
    _collection = "lists"

    name = field.Char()
    auth_url = field.Char()
    thanks_url = field.Char()

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
