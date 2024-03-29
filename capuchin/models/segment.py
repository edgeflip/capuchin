import humongolus as orm
from flask import url_for
from humongolus import field

from capuchin import config
from capuchin import filters
from capuchin import db
from capuchin.models.client import Client
from capuchin.models.user import User


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
    def id(self):
        return self._id

    @property
    def url(self):
        return url_for('audience.id', id=str(self._id))

    def add_filter(self, key, value):
        key = key.replace(".", "___")#can't store fieldnames with dot notation
        self.filters[key] = value
        self._get('filters')._dirty = None

    def build_query_filters(self, sort=None):
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
                    f = filters.FILTER_TYPES[filt['type']](k,v,client=str(self.client._id))
                    if f: and_.append(f)
                except Exception as e:
                    self.logger.exception(e)

        query = {"filtered":{"filter":{"and":and_}}}
        self.logger.info(query)
        return query

    def get_records(self, filters, from_=0, sort=None):
        q = {}
        if sort: q['sort'] = sort
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

    def sort(self, sort):
        if sort:
            return {
                sort[0]:{
                    "order":sort[1]
                }
            }

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

    def records(self, q="*", from_=0, size=config.RECORDS_PER_PAGE, sort=None):
        sort = self.sort(sort)
        filters = self.build_query_filters()
        return self.get_records(filters, from_, sort)

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

    @property
    def engagement(self):
        q = {
            "aggregations": {
                "eng": { "avg": { "field": "engagement" } },
            },
            "query": self.build_query_filters(),
        }
        ES = db.init_elasticsearch()
        res = ES.search(
            config.ES_INDEX,
            config.USER_RECORD_TYPE,
            _source=False,
            size=0,
            body=q,
        )
        return res.get("aggregations", {}).get("eng", {}).get("value", None)


Client.segments = orm.Lazy(type=Segment, key='client')
