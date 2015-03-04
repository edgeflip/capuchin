from capuchin.models import ESObject
from capuchin import config
from flask import url_for

class Post(ESObject):
    TYPE = config.POST_RECORD_TYPE

    def url(self):
        return url_for('engagement.view', id=self.id)

    @classmethod
    def filter(cls, client, q, sort):
        q = {
            "query":{
                "query_string":{
                    "default_field":"message",
                    "query":q
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
