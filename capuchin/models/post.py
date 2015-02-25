from capuchin import config
from capuchin import db
from slugify import slugify
import logging

class Post(object):

    def __init__(self, id=None, data=None):
        if id:
            ES = db.init_elasticsearch()
            data = ES.get(
                config.ES_INDEX,
                id,
                config.POST_RECORD_TYPE,
            )
        self.populate(data)

    def populate(self, data):
        if data:
            for k,v in data['_source'].iteritems():
                setattr(self, k, v)

    def populate_fields(self, data):
        self.fields = data['fields'].keys()
        for k,v in data['fields'].iteritems():
            setattr(self, slugify(k), v[0])

    def json(self):
        ret = {}
        for f in self.fields:
            ret[slugify(f)] = getattr(self, slugify(f))

        return ret

    @classmethod
    def get_records(cls, q, from_=0, size=config.RECORDS_PER_PAGE):
        ES = db.init_elasticsearch()
        res = ES.search(
            config.ES_INDEX,
            config.POST_RECORD_TYPE,
            fields=config.POST_RECORD_FIELDS,
            size=size,
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
    def records(cls, client, q="*", from_=0, size=config.RECORDS_PER_PAGE, ret_obj=False):
        q = cls.filter(client, q)
        res = cls.get_records(q, from_, size=size)
        ret = []
        if ret_obj:
            for p in res['hits']:
                po = Post()
                po.populate_fields(p)
                ret.append(po)
            return ret

        return res

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
