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

def create_ages(buckets):
    last = buckets[0]['key']
    ages = collections.OrderedDict()
    ages["< {}".format(last)] = None
    for i in buckets[1:]:
        ages["{}-{}".format(last, i['key'])] = i['doc_count']
        last=i['key']+1
    ages["{}+".format(last)] = None
    return ages

class SegmentsDefault(MethodView):

    def get(self):
        return render_template("segments/index.html")

class SegmentsCreate(MethodView):

    def get(self):
        aggs = current_app.es.search(
            config.ES_INDEX,
            "user",
            _source=False,
            fields=['fname', 'lname', 'age', 'fbid', 'last_activity', 'city', 'state'], 
            body={
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
        )
        logging.info(aggs['hits'])
        return render_template(
            "segments/create.html",
            ages=create_ages(aggs['aggregations']['ages']['buckets']),
            states=aggs['aggregations']['states'],
            popularity=aggs['aggregations']['popularity'],
            people=aggs['hits']['hits'],
        )

segments.add_url_rule("/segments", view_func=SegmentsDefault.as_view('segments'))
segments.add_url_rule("/segments/create", view_func=SegmentsCreate.as_view('segments_create'))
