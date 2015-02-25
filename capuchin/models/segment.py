import humongolus as orm
import humongolus.field as field
from capuchin import config
from capuchin import filters
from capuchin import db
from capuchin.models.client import Client

class Segment(orm.Document):
    _db = "capuchin"
    _collection = "segments"
    _indexes = [
        orm.Index('client', key=('client', 1)),
    ]
    name = field.Char()
    filters = orm.Field(default={})
    client = field.DocumentId(type=Client)

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
            if v: and_.append(filters.FILTER_TYPES[filt['type']](k,v))

        query = {"filtered":{"filter":{"and":and_}}}
        self.logger.info(query)
        return query

    def get_records(self, filters, from_=0):
        q = {}
        if len(filters['filtered']['filter']['and']): q["query"] = filters
        ES = db.init_elasticsearch()
        res = ES.search(
            config.ES_INDEX,
            config.USER_RECORD_TYPE,
            fields=config.USER_RECORD_FIELDS,
            size=config.RECORDS_PER_PAGE,
            from_=from_,
            _source=False,
            body=q
        )
        return res['hits']

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
        return res["aggregations"]

    def get_lists(self):
        q = {"aggregations":{}}
        for f in filters.FILTERS:
            if f["type"] == "term_list":
                key = f["display"]
                q["aggregations"][key] = {
                    "terms":{"field":f["field"]}
                }
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

    @property
    def last_notification(self):
        alert = self.notifications().sort('__created__', -1).limit(1)
        if alert.count():
            self.logger.info(alert[0])
            return alert[0]
        return None

Client.segments = orm.Lazy(type=Segment, key='client')
