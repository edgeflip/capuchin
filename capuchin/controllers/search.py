import json
import logging
import math

from bson.objectid import InvalidId
from flask import (
    Blueprint,
    Response,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask.ext.login import current_user
from flask.views import MethodView

from capuchin import config
from capuchin import filters
from capuchin.controllers.tables import render_table
from capuchin.models.imports import ImportOrigin
from capuchin.models.interest import Interest
from capuchin.models.segment import Segment
from capuchin.models.user import User
from capuchin.models.notification import Notification
from capuchin.models.post import Post
from capuchin.views.tables.audience import Users, Segments, SegmentUsers


search = Blueprint(
    'search',
    __name__,
    template_folder=config.TEMPLATES,
    url_prefix="/search",
)

class Search(MethodView):

    def get(self):
        q = request.args.get('q')
        posts = Post.search(current_user.client, q)
        users = User.search(current_user.client, q)
        segments = Segment.search(current_user.client, q)
        notifications = Notification.search(current_user.client, q)
        logging.info(posts)
        logging.info(users)
        logging.info(segments)
        logging.info(notifications)
        return Response()

search.add_url_rule("/", view_func=Search.as_view("index"))
