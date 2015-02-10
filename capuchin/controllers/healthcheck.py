from flask import Blueprint, render_template, request, Response
from flask.views import MethodView
from flask.ext.login import current_user
from capuchin import INFLUX
from capuchin import config
from capuchin.models.list import List
from capuchin.models.segment import Segment
import logging
import json

hc = Blueprint(
    'healthcheck',
    __name__,
    template_folder=config.TEMPLATES,
)

class HealthCheck(MethodView):

    def get(self):
        logging.info("healthcheck!")
        return Response()

hc.add_url_rule("/healthcheck", view_func=HealthCheck.as_view('healthcheck'))
