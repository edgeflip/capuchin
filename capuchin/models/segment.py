import humongolus as orm
import humongolus.field as field
from capuchin import config
from capuchin import filters
from capuchin import ES

class Segment(orm.Document):
    _db = "capuchin"
    _collection = "segments"
    name = field.Char()
    filters = orm.Field(default={})

    def add_filter(self, key, value):
        self.filters[key] = value
        self._get('filters')._dirty = None

    def build_query_filters(self):
        and_ = []
        for k,v in self.filters.iteritems():
            filt = filters.get_filter(filters.FILTERS, k)
            if v: and_.append(filters.FILTER_TYPES[filt['type']](k,v))

        query = {"filtered":{"filter":{"and":and_}}}
        return query

    def get_records(self, filters, from_=0):
        q = {}
        if len(filters['filtered']['filter']['and']): q["query"] = filters
        res = ES.search(
            config.ES_INDEX,
            config.RECORD_TYPE,
            fields=config.RECORD_FIELDS,
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
        res = ES.search(
            config.ES_INDEX,
            config.RECORD_TYPE,
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
        res = ES.search(
            config.ES_INDEX,
            config.RECORD_TYPE,
            _source=False,
            size=0,
            body=q,
        )
        return res["aggregations"]

    def records(self, from_=0):
        filters = self.build_query_filters()
        return self.get_records(filters, from_)

    def count(self):
        filters = self.build_query_filters()
        q = None
        self.logger.info(filters)
        if len(filters['filtered']['filter']['and']):
            q = {}
            q["query"] = filters
        res = ES.count(
            config.ES_INDEX,
            config.RECORD_TYPE,
            body=q
        )
        return res['count']
