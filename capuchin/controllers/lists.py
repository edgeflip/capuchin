from flask import Blueprint, render_template
from flask.views import MethodView
from capuchin import config

lists = Blueprint(
    'lists',
    __name__,
    template_folder=config.TEMPLATES,
)

class ListsDefault(MethodView):

    def get(self):
        return render_template("lists/index.html")

class ListsCreate(MethodView):

    def get(self):
        return render_template("lists/create.html")

lists.add_url_rule("/lists", view_func=ListsDefault.as_view('lists'))
lists.add_url_rule("/lists/create", view_func=ListsCreate.as_view('lists_create'))
