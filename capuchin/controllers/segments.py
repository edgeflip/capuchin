from flask import Blueprint, render_template, current_app, redirect, url_for
from flask.views import MethodView
from capuchin import config
import collections
import logging
import math

RECORDS_PER_PAGE = 10

segments = Blueprint(
    'segments',
    __name__,
    template_folder=config.TEMPLATES,
)

def age_query(q, fro, to):
    q['filtered']['filter']['and'].append(
        {
            "range":{
                "age":{
                    "from":fro,
                    "to":to
                }
            }
        }
    )
    return q

def state_query(q, fro, to):
    q['filtered']['filter']['and'].append({"term":{ "state":fro}})
    return q

def popularity_query(q, fro, to):
    q['filtered']['filter']['and'].append(
        {
            "range":{
                "num_friends_interacted_with_my_posts":{
                    "from":fro,
                }
            }
        }
    )
    return q

FILTER_TYPES = {
    "age":age_query,
    "state":state_query,
    "popularity":popularity_query
}

def has_filter(query, filter_type):
    for f in query['filtered']['filter']['and']:
        if f.get('range'):
            if f['range'].get('age') and filter_type == 'age':
                return f['range'].get('age')
            elif filter_type == 'popularity':
                return f['range'].get('num_friends_interacted_with_my_posts')
        elif f.get('term') and filter_type == 'state': return f.get('term')['state']

    return False

segments.add_app_template_filter(has_filter)

def create_ages(buckets):
    last = buckets[0]['key']
    ages = collections.OrderedDict()
    ages["bucket{}".format(last)] = {
        "display":"< {}".format(last),
        "range":{"from":0, "to":last},
        "count": buckets[0]['doc_count']
    }
    for i in buckets[1:]:
        ages["bucket{}".format(i['key'])] = {
            "display": "{}-{}".format(last, i['key']),
            "range": {"from":last, "to":i['key']},
            "count": i['doc_count'],
        }
        last=i['key']+1
    ages["bucket{}".format(last)] = {
        "display": "{}+".format(last),
        "range": {"from":last},
        "count": "NA"

    }
    return ages

def create_pagination(total_records, current_page=0):
    tp = math.ceil(total_records/RECORDS_PER_PAGE)
    total_pages = tp if tp <= 20 else 20
    page = {
        "previous": current_page-1 if current_page > 0 else 0,
        "next": current_page+1 if current_page < total_pages else total_pages,
        "total_pages": int(total_pages)
    }
    return page


def get_aggs(query=None, fro=0):
    body = {
        "aggregations" : {
            "ages" : {
                "histogram" : {
                    "field" : "age",
                    "interval" : 10,
                    "min_doc_count" : 0
                }
            },
            "states" : {
                "terms" : {
                    "field" : "state",
                    "size": 50,
                }
            },
            "popularity": {
                "histogram" : {
                    "field" : "num_friends_interacted_with_my_posts",
                    "interval" : 100,
                    "min_doc_count": 100,
                    "extended_bounds" : {
                        "min" : 100,
                        "max" : 5000
                    }
                }
            }
        }
    }
    if query and len(query['filtered']['filter']['and']): body['query'] = query
    logging.info(body)
    aggs = current_app.es.search(
        config.ES_INDEX,
        "user",
        _source=False,
        fields=['fname', 'lname', 'age', 'fbid', 'last_activity', 'city', 'state'],
        body=body,
        from_=fro,
        size=RECORDS_PER_PAGE,
    )
    return aggs

class SegmentsDefault(MethodView):

    def get(self):
        return render_template("segments/index.html")

class SegmentsCreate(MethodView):

    def get(self, id=None):
        if id:
            res = current_app.es.get(config.ES_INDEX, id, "segment")
            q = res['_source']
        else:
            q = {
                "filtered":{
                    "filter":{
                        "and":[]
                    }
                }
            }
            res = current_app.es.index(config.ES_INDEX, "segment", body=q)
            return redirect(url_for(".segments_create_id", id=res['_id']))

        aggs = get_aggs(query=q)
        return render_template(
            "segments/create.html",
            ages=create_ages(aggs['aggregations']['ages']['buckets']),
            states=aggs['aggregations']['states'],
            popularity=aggs['aggregations']['popularity'],
            people=aggs['hits']['hits'],
            id=res['_id'],
            query=q,
            total=aggs['hits']['total'],
            pagination=create_pagination(aggs['hits']['total']),
        )


class SegmentsUpdate(MethodView):

    def get(self, id, filter_type, fro=None, to=None):
        res = current_app.es.get(config.ES_INDEX, id, "segment")
        q = res['_source']
        q = FILTER_TYPES[filter_type](q, fro, to)
        current_app.es.index(config.ES_INDEX, "segment", body=q, id=id)
        aggs = get_aggs(query=q)
        return render_template(
            "segments/filtered.html",
            ages=create_ages(aggs['aggregations']['ages']['buckets']),
            states=aggs['aggregations']['states'],
            popularity=aggs['aggregations']['popularity'],
            people=aggs['hits']['hits'],
            id=res['_id'],
            query=q,
            total=aggs['hits']['total'],
            pagination=create_pagination(aggs['hits']['total']),
        )

class SegmentsPagination(MethodView):

    def get(self, id, page):
        res = current_app.es.get(config.ES_INDEX, id, "segment")
        q = res['_source']
        aggs = get_aggs(query=q, fro=int(page)*RECORDS_PER_PAGE)
        return render_template(
            "segments/people.html",
            people=aggs['hits']['hits'],
        )

segments.add_url_rule("/segments", view_func=SegmentsDefault.as_view('segments'))
segments.add_url_rule("/segments/create", view_func=SegmentsCreate.as_view('segments_create'))
segments.add_url_rule("/segments/create/<id>", view_func=SegmentsCreate.as_view('segments_create_id'))
segments.add_url_rule("/segments/<id>/filters/<filter_type>/<fro>/<to>", view_func=SegmentsUpdate.as_view("filter_update"))
segments.add_url_rule("/segments/<id>/page/<page>", view_func=SegmentsPagination.as_view("segment_pagination"))
