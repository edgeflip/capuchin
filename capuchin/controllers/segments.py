from flask import Blueprint, render_template, current_app, redirect, url_for, request, Response
from flask.views import MethodView
from flask.ext.login import current_user
from capuchin import config
from capuchin import filters
from capuchin.models.segment import Segment
from capuchin.app import ES
import logging
import slugify
import math
import json

segments = Blueprint(
    'segments',
    __name__,
    template_folder=config.TEMPLATES,
)

def create_pagination(total_records, current_page=0):
    tp = math.ceil(total_records/config.RECORDS_PER_PAGE)
    total_pages = tp if tp <= 20 else 20
    page = {
        "previous": current_page-1 if current_page > 0 else 0,
        "next": current_page+1 if current_page < total_pages else total_pages,
        "total_pages": int(total_pages)
    }
    return page

def get_segment(id):
    if id:
        s = Segment(id=id)
    else:
        s = Segment()
        s.client = current_user.client
        id = s.save()
    return (s, id,)

def get_suggestions(field, text):
    q = {}
    res = ES.search(
        config.ES_INDEX,
        config.RECORD_TYPE,
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
                        #"order" : { "_term" : "asc" },
                    }
                }
            }
        }
    )
    return res['aggregations']

def update_segment(id, filters):
    s = Segment(id=id)
    for k,v in filters.iteritems():
        s.add_filter(k,v)
    s.save()
    return s

class SegmentsDefault(MethodView):

    def get(self):
        segments = current_user.client.segments(query={"name":{"$ne":None}})
        return render_template("segments/index.html", segments=segments)

class SegmentsCreate(MethodView):

    def get(self, id=None, page=0, template=None):
        segment, _id = get_segment(id)
        if not id: return redirect(url_for(".id", id=_id))
        records = segment.records(from_=page*config.RECORDS_PER_PAGE)
        tmpl = template if template else "segments/create.html"
        lists = segment.get_lists()
        logging.info(lists)
        return render_template(
            tmpl,
            filters=filters.FILTERS,
            filters_json=json.dumps(segment.filters),
            values=segment.filters,
            ranges=segment.get_ranges(),
            lists=lists,
            records=records['hits'],
            id=id,
            total=records['total'],
            pagination=create_pagination(records['total'], page),
            name=segment.name,
            page=page
        )

    def post(self, id, page=0):
        filters = json.loads(request.form['filters'])
        logging.info(filters)
        q = update_segment(id, filters)
        return self.get(id=id, page=page, template="segments/records.html")

class SegmentsAutocomplete(MethodView):

    def get(self, field):
        term = request.args.get("term")
        res = get_suggestions(field, term)
        ar = [{"label":u"{}".format(a['key']), "value":a['key']} for a in res[field]['buckets']]
        return Response(json.dumps(ar), mimetype='application/json')

class SegmentsSave(MethodView):

    def post(self, id, page=0):
        s = Segment(id=id)
        s.name = request.form['name']
        s.save()
        return render_template("widgets/notification.html", message=('success','Segment Saved'))

segments.add_url_rule("/segments", view_func=SegmentsDefault.as_view('index'))
segments.add_url_rule("/segments/create", view_func=SegmentsCreate.as_view('create'))
segments.add_url_rule("/segments/<id>", view_func=SegmentsCreate.as_view('id'))
segments.add_url_rule("/segments/<id>/<int:page>", view_func=SegmentsCreate.as_view("page"))
segments.add_url_rule("/segments/<id>/<int:page>/filters", view_func=SegmentsCreate.as_view("filter_update"))
segments.add_url_rule("/segments/autocomplete/<field>", view_func=SegmentsAutocomplete.as_view("autocomplete"))
segments.add_url_rule("/segments/<id>/save", view_func=SegmentsSave.as_view("save"))
