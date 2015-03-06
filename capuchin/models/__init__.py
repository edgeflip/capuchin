from capuchin import config
from capuchin import db
from slugify import slugify
from bunch import Bunch
import logging

class ESObject(Bunch):

    TYPE = None

    def __init__(self, id=None, data=None):
        if id:
            ES = db.init_elasticsearch()
            data = ES.get(
                config.ES_INDEX,
                id,
                self.TYPE,
            )
            data = data['_source']

        super(ESObject, self).__init__(**data)

    @classmethod
    def save(cls, data):
        ES = db.init_elasticsearch()
        res = ES.index(index=config.ES_INDEX, doc_type=cls.TYPE, body=data, id=data.efid)

    @classmethod
    def get_records(cls, q, from_=0, size=10):
        ES = db.init_elasticsearch()
        res = ES.search(
            config.ES_INDEX,
            cls.TYPE,
            size=size,
            from_=from_,
            body=q
        )
        b = Bunch.fromDict(res['hits'])
        b.hits = [cls(data=d['_source']) for d in b.hits]
        return b

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
                    "clients.id":str(client._id)
                }
            },
            "sort":sort
        }
        return q



    @classmethod
    def sort(cls, sort=None):
        if sort:
            return {
                sort[0]:{
                    "order":sort[1]
                }
            }
        return {}

    @classmethod
    def records(cls, client, q="*", from_=0, size=config.RECORDS_PER_PAGE, sort=None):
        sort = cls.sort(sort)
        q = cls.filter(client, q, sort)
        return cls.get_records(q, from_, size=size)

    @classmethod
    def count(cls, client):
        ES = db.init_elasticsearch()
        q = {
            "query":{
                "term":{
                    "clients.id":str(client._id),
                }
            }
        }
        res = ES.count(
            config.ES_INDEX,
            cls.TYPE,
            body=q
        )
        return res['count']
