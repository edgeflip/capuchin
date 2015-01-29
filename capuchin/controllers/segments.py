from flask import Blueprint, render_template, current_app, redirect, url_for, request, Response
from flask.views import MethodView
from capuchin import config
import logging
import math
import json

RECORDS_PER_PAGE = 10

segments = Blueprint(
    'segments',
    __name__,
    template_folder=config.TEMPLATES,
)

RECORD_TYPE = "user"

RECORD_FIELDS = ["fname", "lname", "age", "fbid", "city", "state"]

FILTERS = [
    {
        "display":"Age",
        "field":"age",
        "type":"range",
        "aggregation_args":{
            "interval":10,
            "min_doc_count":0,
            "interval":1,
        }
    },
    {
        "display":"Popularity",
        "field":"num_friends_interacted_with_my_posts",
        "type":"range",
        "aggregation_args":{
            "interval" : 100,
            "min_doc_count": 100,
            "extended_bounds" : {
                "min" : 100,
                "max" : 5000
            }
        }
    },
    {
        "display":"State",
        "field":"state",
        "type":"term",
        "aggregation_args":{}
    },
    {
        "display":"Religion",
        "field":"religion",
        "type":"term",
        "aggregation_args":{}
    },
]

def range_filter(field, value):
    return {
        "range":{
            field:{
                "from":value[0],
                "to": value[1]
            }
        }
    }

def term_filter(field, value):
    return {
        "term":{
            "{}.facet".format(field):value
        }
    }

FILTER_TYPES = {
    "range": range_filter,
    "term": term_filter,
}

def get_filter(filters, field):
    for f in filters:
        if f['field'] == field: return f

def create_pagination(total_records, current_page=0):
    tp = math.ceil(total_records/RECORDS_PER_PAGE)
    total_pages = tp if tp <= 20 else 20
    page = {
        "previous": current_page-1 if current_page > 0 else 0,
        "next": current_page+1 if current_page < total_pages else total_pages,
        "total_pages": int(total_pages)
    }
    return page

def get_ranges(filters):
    q = {"aggregations":{}}
    for f in filters:
        if f["type"] == "range":
            key = f["display"]
            q["aggregations"][key] = {
                "stats":{
                    "field":f["field"]
                }
            }
    res = current_app.es.search(
        config.ES_INDEX,
        "user",
        _source=False,
        size=0,
        body=q,
    )
    return res["aggregations"]

def get_filters(id):
    if id:
        res = current_app.es.get(config.ES_INDEX, id, "segment")
        q = res['_source']
    else:
        q = {}
        res = current_app.es.index(config.ES_INDEX, "segment", body=q)
        id = res['_id']
    return (q, id,)

def get_records(filters, from_=0):
    q = {}
    if len(filters['filtered']['filter']['and']): q["query"] = filters
    res = current_app.es.search(
        config.ES_INDEX,
        RECORD_TYPE,
        fields=RECORD_FIELDS,
        size=RECORDS_PER_PAGE,
        from_=from_,
        _source=False,
        body=q
    )
    return res['hits']

def get_suggestions(field, text):
    q = {}
    res = current_app.es.search(
        config.ES_INDEX,
        RECORD_TYPE,
        size=0,
        _source=False,
        body={
            "query": {
                "match": {
                    "{}.suggest".format(field): {
                        "query":text,
                        "analyzer":"lowercase"
                    }
                }
            },
            "aggregations":{
                field:{
                    "terms":{
                        "field":"{}.facet".format(field),
                        "size":20,
                        "order" : { "_term" : "asc" },
                    }
                }
            }
        }
    )
    return res['aggregations']

def update_filters(id, filters):
    res = current_app.es.get(config.ES_INDEX, id, "segment")
    q = res['_source']
    for k,v in filters.iteritems(): q[k] = v
    current_app.es.index(config.ES_INDEX, "segment", body=q, id=id)
    return q

def build_query_filters(filters):
    and_ = []
    for k,v in filters.iteritems():
        filt = get_filter(FILTERS, k)
        logging.info(k)
        logging.info(filt)
        if v: and_.append(FILTER_TYPES[filt['type']](k,v))

    query = {"filtered":{"filter":{"and":and_}}}
    return query

class SegmentsDefault(MethodView):

    def get(self):
        return render_template("segments/index.html")

class SegmentsCreate(MethodView):

    def get(self, id=None, page=0, template=None):
        filters, _id = get_filters(id)
        if not id: return redirect(url_for(".segments_id", id=_id))
        query_filters = build_query_filters(filters)
        ranges = get_ranges(FILTERS)
        records = get_records(query_filters, from_=page*RECORDS_PER_PAGE)
        logging.info(ranges)
        tmpl = template if template else "segments/create.html"
        return render_template(
            tmpl,
            filters=FILTERS,
            values=filters,
            ranges=ranges,
            records=records['hits'],
            id=id,
            total=records['total'],
            pagination=create_pagination(records['total'], page),
            page=page
        )

    def post(self, id, page=0):
        filters = json.loads(request.form['filters'])
        q = update_filters(id, filters)
        return self.get(id=id, page=page, template="segments/records.html")

class SegmentsAutocomplete(MethodView):

    def get(self, field):
        term = request.args.get("term")
        res = get_suggestions(field, term)
        ar = [{"label":u"{}: {}".format(a['key'], a['doc_count']), "value":a['key']} for a in res[field]['buckets']]
        return Response(json.dumps(ar), mimetype='application/json')

segments.add_url_rule("/segments", view_func=SegmentsDefault.as_view('segments'))
segments.add_url_rule("/segments/create", view_func=SegmentsCreate.as_view('segments_create'))
segments.add_url_rule("/segments/<id>", view_func=SegmentsCreate.as_view('segments_id'))
segments.add_url_rule("/segments/<id>/<int:page>", view_func=SegmentsCreate.as_view("segments_page"))
segments.add_url_rule("/segments/<id>/<int:page>/filters", view_func=SegmentsCreate.as_view("filter_update"))
segments.add_url_rule("/segments/autocomplete/<field>", view_func=SegmentsAutocomplete.as_view("autocomplete"))
