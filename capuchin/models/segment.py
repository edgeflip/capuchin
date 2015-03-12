from flask import url_for
import humongolus as orm
import humongolus.field as field
from capuchin import config
from capuchin import filters
from capuchin import db
from capuchin.models.client import Client
from capuchin.models.user import User
from bunch import Bunch

class Segment(orm.Document):
    _db = "capuchin"
    _collection = "segments"
    _indexes = [
        orm.Index('client', key=('client', 1)),
    ]
    name = field.Char()
    filters = orm.Field(default={})
    client = field.DocumentId(type=Client)
    last_notification = field.Date()

    @property
    def url(self):
        return url_for('audience.id', id=str(self._id))

    def add_filter(self, key, value):
        key = key.replace(".", "___")#can't store fieldnames with dot notation
        self.filters[key] = value
        self._get('filters')._dirty = None

    def build_query_filters(self):
        and_ = [{
            "term": {
                "clients.id": str(self.client._id)
            }
        }]
        for k,v in self.filters.iteritems():
            k = k.replace("___", ".")#can't store fieldnames with dot notation, restore for query
            filt = filters.get_filter(filters.FILTERS, k)
            if v:
                try:
                    and_.append(filters.FILTER_TYPES[filt['type']](k,v))
                except:pass

        query = {"filtered":{"filter":{"and":and_}}}
        self.logger.info(query)
        return query

    def get_records(self, filters, from_=0):
        q = {}
        if len(filters['filtered']['filter']['and']): q["query"] = filters
        return User.get_records(q, from_)

    def get_ranges(self):
        q = {"aggregations":{}}
        for f in filters.FILTERS:
            if f["type"] == "range":
                key = f["display"]
                q["aggregations"][key] = {
                    "stats":{
                        "field":f["field"]
                    }
                }
        ES = db.init_elasticsearch()
        res = ES.search(
            config.ES_INDEX,
            config.USER_RECORD_TYPE,
            _source=False,
            size=0,
            body=q,
        )
        return res.get("aggregations", {})

    def get_lists(self):
        q = {"aggregations":{}}
        for f in filters.FILTERS:
            if f["type"] == "term_list":
                key = f["display"]
                q["aggregations"][key] = {
                    "terms":{"field":f["field"]}
                }
        if not q["aggregations"].keys(): return {}
        ES = db.init_elasticsearch()
        res = ES.search(
            config.ES_INDEX,
            config.USER_RECORD_TYPE,
            _source=False,
            size=0,
            body=q,
        )
        return res["aggregations"]

    def records(self, from_=0):
        filters = self.build_query_filters()
        return self.get_records(filters, from_)

    @property
    def count(self):
        filters = self.build_query_filters()
        q = None
        self.logger.info(filters)
        if len(filters['filtered']['filter']['and']):
            q = {}
            q["query"] = filters
        ES = db.init_elasticsearch()
        res = ES.count(
            config.ES_INDEX,
            config.USER_RECORD_TYPE,
            body=q
        )
        return res['count']

Client.segments = orm.Lazy(type=Segment, key='client')
