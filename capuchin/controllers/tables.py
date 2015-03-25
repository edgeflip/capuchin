from flask import Blueprint, render_template, current_app, redirect, url_for, request, Response, g, session
from flask.views import MethodView
from flask.ext.login import current_user
from capuchin import config
from capuchin import filters
from capuchin.models.segment import Segment
from capuchin.views.tables import Table
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
    return table

def get_args(cls_name):
    other = request.base_url.split("/")[-1]
    if not other: other = request.base_url.split("/")[-2]
    obj = request.args.get('obj', other)
    session_key = "{}{}".format(obj, cls_name.replace(".", "___"))
    if not request.args.get('field'):
        logging.info("KEY: {}".format(session_key))
        logging.info("SESSION: {}".format(session))
        args = session.get(session_key)
        logging.info("ARGS: {}".format(args))
    else:
        args = {}
        args['field'] = request.args.get('field')
        args['dir'] = request.args.get('dir')
        args['page'] = int(request.args.get('page', 1))
        args['size'] = int(request.args.get('size', 10))
        args['obj'] = request.args.get('obj')
        try:
            args['q'] = json.loads(request.args['q'])
        except:
            args['q'] = request.args['q']
        args['from_'] = args['size']*(args['page']-1)
        args['pagination'] = bool(request.args['pagination'])
        session[session_key] = args
    return args

def render_table(cls):
    if not isinstance(cls, basestring):
        cls_name = ".".join("{}.{}".format(
            cls.__module__,
            cls.__name__
        ).split(".")[3:])
        table = cls
    else:
        table = get_table(cls)
        cls_name = cls

    args = get_args(cls_name)
    if not args: return None

    try:
        t = table(current_user.client, args['obj'])
        ret = t.render(
            sort=(args['field'], args['dir']),
            q=args['q'],
            size=args['size'],
            from_=args['from_'],
            pagination=args['pagination']
        )
        return ret
    except ImportError as e:
        logging.exception(e)

class TableOrder(MethodView):

    def get(self, cls):
        return Response(render_table(cls))

tables.add_url_rule("/<cls>", view_func=TableOrder.as_view('index'))
