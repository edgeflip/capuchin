from flask import Blueprint, render_template
from flask.views import MethodView
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
        lists = List.find()
        segments = Segment.find({"name":{"$ne":None}})
        return render_template("dashboard/index.html", lists=lists, segments=segments)

db.add_url_rule("/", view_func=DashboardDefault.as_view('index'))
