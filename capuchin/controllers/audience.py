from flask import Blueprint, render_template, current_app, redirect, url_for, request, Response, g
from flask.views import MethodView
from flask.ext.login import current_user
from capuchin import config
from capuchin import filters
from capuchin.models.segment import Segment
from capuchin.models.interest import Interest
from capuchin.models.user import User
from capuchin.views.tables.audience import Users, Segments, SegmentUsers
import logging
import slugify
import math
import json

audience = Blueprint(
    'audience',
    __name__,
    template_folder=config.TEMPLATES,
    url_prefix="/audience",
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
        if id == 'all':
            s = Segment(data={'client':current_user.client})
        else:
            s = Segment(id=id)
    else:
        s = Segment()
        s.client = current_user.client
        id = s.save()
    return (s, id,)

def get_suggestions(field, text):
    q = {}
    res = g.ES.search(
        config.ES_INDEX,
        config.USER_RECORD_TYPE,
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

def update_segment(id, filters, name):
    s = Segment(id=id)
    s.name = name
    for k,v in filters.iteritems():
        s.add_filter(k,v)
    s.save()
    return s

class Default(MethodView):

    def get(self):
        return render_template(
            "audience/index.html",
            segments=Segments(current_user.client),
            users=Users(current_user.client),
        )

class View(MethodView):

    def get(self, id):
        person = User(id=id)
        return render_template(
            "audience/view.html",
            person=person
        )

class Create(MethodView):

    def get(self, id=None, page=0, template=None):
        segment, _id = get_segment(id)
        if not id: return redirect(url_for(".id", id=_id))
        users = SegmentUsers(current_user.client, str(_id))
        tmpl = template if template else "audience/create.html"
        lists = segment.get_lists()
        interests = Interest.find()
        fs = {}
        for k,v in segment.filters.iteritems():
            k = k.replace("___", ".")
            fs[k] = v
        return render_template(
            tmpl,
            interests=interests,
            filters=filters.FILTERS,
            filters_json=json.dumps(fs),
            values=segment.filters,
            ranges=segment.get_ranges(),
            lists=lists,
            users=users,
            id=id,
            name=segment.name if segment.name else "New Segment",
            page=page
        )

    def post(self, id, page=0):
        filters = json.loads(request.form.get('filters', '{}'))
        logging.info(filters)
        name = request.form.get('name')
        if id!='all': q = update_segment(id, filters, name)
        return self.get(id=id, page=page, template="audience/records.html")

class Autocomplete(MethodView):

    def get(self, field):
        term = request.args.get("term")
        res = get_suggestions(field, term)
        ar = [{"label":u"{}".format(a['key']), "value":a['key']} for a in res[field]['buckets']]
        return Response(json.dumps(ar), mimetype='application/json')

class Save(MethodView):

    def post(self, id, page=0):
        s = Segment(id=id)
        s.name = request.form['name']
        s.save()
        return render_template("widgets/notification.html", message=('success','Segment Saved'))

audience.add_url_rule("/", view_func=Default.as_view('index'))
audience.add_url_rule("/segment/create", view_func=Create.as_view('create'))
audience.add_url_rule("/segment/<id>", view_func=Create.as_view('id'))
audience.add_url_rule("/segment/<id>/<int:page>", view_func=Create.as_view("page"))
audience.add_url_rule("/segment/<id>/<int:page>/filters", view_func=Create.as_view("filter_update"))
audience.add_url_rule("/segment/autocomplete/<field>", view_func=Autocomplete.as_view("autocomplete"))
audience.add_url_rule("/segment/<id>/save", view_func=Save.as_view("save"))
audience.add_url_rule("/view/<id>", view_func=View.as_view("view"))
