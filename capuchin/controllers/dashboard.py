from flask import Blueprint, render_template, request
from flask.views import MethodView
from flask.ext.login import current_user
from capuchin import config
from capuchin.models.list import List
from capuchin.models.segment import Segment

db = Blueprint(
    'dashboard',
    __name__,
    template_folder=config.TEMPLATES,
)

class DashboardDefault(MethodView):

    def get(self):
        first = request.args.get("first")
        lists = current_user.client.lists()
        segments = current_user.client.segments(query={"name":{"$ne":None}})
        return render_template("dashboard/index.html", lists=lists, segments=segments, first=first)

db.add_url_rule("/", view_func=DashboardDefault.as_view('index'))
