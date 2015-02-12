from capuchin import config
from capuchin import db

class Post(object):

    @classmethod
    def get_records(cls, q, from_=0):
        ES = db.init_elasticsearch()
        res = ES.search(
            config.ES_INDEX,
            config.POST_RECORD_TYPE,
            fields=config.POST_RECORD_FIELDS,
            size=config.RECORDS_PER_PAGE,
            from_=from_,
            _source=False,
            body=q
        )
        return res['hits']

    @classmethod
    def filter(cls, client, q):
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
            "sort":{
                "created_time":{
                    "order": "desc"
                }
            }
        }
        return q

    @classmethod
    def records(cls, client, q="*", from_=0):
        q = cls.filter(client, q)
        return cls.get_records(q, from_)

    @classmethod
    def count(cls, client):
        ES = db.init_elasticsearch()
        q = cls.filter(client, "*")
        res = ES.count(
            config.ES_INDEX,
            config.POST_RECORD_TYPE,
            body=q
        )
        return res['count']
