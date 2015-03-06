from flask import Blueprint, render_template, current_app, redirect, url_for, request, Response, g
from flask.views import MethodView
from flask.ext.login import current_user
from capuchin import config
from capuchin import filters
from capuchin.models.segment import Segment
import urllib
import logging
import slugify
import math
import json

tables = Blueprint(
    'tables',
    __name__,
    template_folder=config.TEMPLATES,
    url_prefix="/tables",
)

table_module = "capuchin.views.tables"

def get_table(cls):
        parts = "{}.{}".format(table_module, cls).split(".")
        logging.info(parts)
        mod = __import__(".".join(parts[:-1]), globals(), locals(), fromlist=[parts[-1]])
        table = getattr(mod, parts[-1])
        t = table(current_user.client)
        return t

class Sort(MethodView):

    def get(self, cls, field, dir):
        try:
            t = get_table(cls)
            try:
                q = json.loads(request.args['q'])
            except Exception as e:
                logging.exception(e)
                q = request.args['q']

            ret = t.render(
                sort=(field, dir),
                q=q,
                size=int(request.args['size']),
                from_=int(request.args['from_']),
                pagination=bool(request.args['pagination'])
            )
            logging.info(t)
            return Response(ret)
        except ImportError as e:
            logging.exception(e)

class Page(MethodView):

    def get(self, cls, field, dir, page):
        size = int(request.args.get('size'))
        from_ = size*(int(page)-1)
        try:
            t = get_table(cls)
            try:
                q = json.loads(request.args['q'])
            except Exception as e:
                logging.exception(e)
                q = request.args['q']

            ret = t.render(
                sort=(field, dir),
                q=q,
                size=size,
                from_=from_
            )
            return Response(ret)
        except ImportError as e:
            logging.exception(e)

tables.add_url_rule("/sort/<cls>/<field>/<dir>", view_func=Sort.as_view('sort'))
tables.add_url_rule("/page/<cls>/<field>/<dir>/<page>", view_func=Page.as_view('page'))
