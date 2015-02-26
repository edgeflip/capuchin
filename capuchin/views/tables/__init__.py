from capuchin import config
from capuchin import db
from slugify import slugify
import logging

class ESResult(object):

    def __init__(self, cls, result):
        for k,v in result.iteritems():
            setattr(self, k, v)

        self.hits = [cls(data=d) for d in self.hits]

class ESObject(object):

    TYPE = None

    def __init__(self, id=None, data=None):
        if id:
            ES = db.init_elasticsearch()
            data = ES.get(
                config.ES_INDEX,
                id,
                self.TYPE,
            )
        self.populate(data)

    def populate(self, data):
        if data:
            for k,v in data['_source'].iteritems():
                setattr(self, k, v)

    def json(self):
        return self.__dict__

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
        return ESResult(cls, res)

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

    @classmethod
    def sort(cls, sort):
        return {
            sort[0]:{
                "order":sort[1]
            }
        }

    @classmethod
    def records(cls, client, q="*", from_=0, size=config.RECORDS_PER_PAGE, sort=('created_time', 'desc')):
        sort = cls.sort(sort)
        q = cls.filter(client, q, sort)
        return cls.get_records(q, from_, size=size)

    @classmethod
    def count(cls, client):
        ES = db.init_elasticsearch()
        q = cls.filter(client, "*")
        res = ES.count(
            config.ES_INDEX,
            cls.TYPE,
            body=q
        )
        return res['count']
