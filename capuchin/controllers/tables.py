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

class Sort(MethodView):

    def get(self, cls, field, dir):
        try:
            parts = cls.split(".")
            if "tables" in parts:
                mod = __import__(".".join(parts[:-1]), globals(), locals(), fromlist=[parts[-1]])
                table = getattr(mod, parts[-1])
                t = table(current_user.client)
                try:
                    q = json.loads(request.args['q'])
                except Exception as e:
                    logging.exception(e)
                    q = request.args['q']

                logging.info(q)
                ret = t.render(
                    sort=(field, dir),
                    q=q,
                    size=request.args['size'],
                    from_=request.args['from_']
                )
                logging.info(t)
                return Response(ret)
        except ImportError as e:
            logging.exception(e)

tables.add_url_rule("/sort/<cls>/<field>/<dir>", view_func=Sort.as_view('sort'))
