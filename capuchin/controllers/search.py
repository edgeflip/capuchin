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
from capuchin.views.tables.audience import Users
from capuchin.views.tables.dashboard import Posts
from capuchin.views.tables.search import Notifications, Segments


search = Blueprint(
    'search',
    __name__,
    template_folder=config.TEMPLATES,
    url_prefix="/search",
)

def get_table(cls, q, sort='__created__'):
    t = render_table(cls)
    if not t:
        t = cls(current_user.client).render(
            q=q,
            sort=(sort, 'desc')
        )

    return t

class Index(MethodView):

    def get(self, page=0):
        q = request.args.get('q') or '*'
        posts = get_table(Posts, q, 'created_time')
        users = get_table(Users, q, 'first_activity')
        segments = get_table(Segments, q)
        notifications = get_table(Notifications, q)

        return render_template(
            'search/results.html',
            posts=posts,
            users=users,
            segments=segments,
            notifications=notifications,
            page=page,
            q=q,
        )

search.add_url_rule("/", view_func=Index.as_view("index"))
