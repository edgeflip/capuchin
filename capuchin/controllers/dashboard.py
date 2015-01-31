from flask import Blueprint, render_template
from flask.views import MethodView
from capuchin import config

db = Blueprint(
    'dashboard',
    __name__,
    template_folder=config.TEMPLATES,
)

class DashboardDefault(MethodView):

    def get(self):
        return render_template("dashboard/index.html")

db.add_url_rule("/", view_func=DashboardDefault.as_view('index'))
