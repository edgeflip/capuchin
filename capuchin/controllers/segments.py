from flask import Blueprint, render_template, current_app
from flask.views import MethodView
from capuchin import config
import collections
import logging

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

def get_aggs(query=None):
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
    if query: body['query'] = query
    logging.info(body)
    aggs = current_app.es.search(
        config.ES_INDEX,
        "user",
        _source=False,
        fields=['fname', 'lname', 'age', 'fbid', 'last_activity', 'city', 'state'],
        body=body
    )
    return aggs

class SegmentsDefault(MethodView):

    def get(self):
        return render_template("segments/index.html")

class SegmentsCreate(MethodView):

    def get(self):
        aggs = get_aggs()
        res = current_app.es.index(config.ES_INDEX, "segment", body={
            "filtered":{
                "filter":{
                    "and":[]
                }
            }
        })
        logging.info(res)
        return render_template(
            "segments/create.html",
            ages=create_ages(aggs['aggregations']['ages']['buckets']),
            states=aggs['aggregations']['states'],
            popularity=aggs['aggregations']['popularity'],
            people=aggs['hits']['hits'],
            id=res['_id']
        )


class SegmentsUpdate(MethodView):

    def get(self, id, filter_type, fro=None, to=None):
        res = current_app.es.get(config.ES_INDEX, id, "segment")
        q = res['_source']
        q = FILTER_TYPES[filter_type](q, fro, to)
        current_app.es.index(config.ES_INDEX, "segment", body=q, id=id)
        logging.info(q)
        aggs = get_aggs(query=q)
        return render_template(
            "segments/filtered.html",
            ages=create_ages(aggs['aggregations']['ages']['buckets']),
            states=aggs['aggregations']['states'],
            popularity=aggs['aggregations']['popularity'],
            people=aggs['hits']['hits'],
            id=res['_id']
        )

segments.add_url_rule("/segments", view_func=SegmentsDefault.as_view('segments'))
segments.add_url_rule("/segments/create", view_func=SegmentsCreate.as_view('segments_create'))
segments.add_url_rule("/segments/<id>/filters/<filter_type>/<fro>/<to>", view_func=SegmentsUpdate.as_view("filter_update"))
