from flask import Blueprint, render_template, request, redirect, url_for
from flask.ext.login import current_user
from flask.views import MethodView
from capuchin import config
from capuchin.models.list import List

lists = Blueprint(
    'lists',
    __name__,
    template_folder=config.TEMPLATES,
    url_prefix="/lists",
)

class ListsDefault(MethodView):

    def get(self):
        lists = [l for l in current_user.client.lists()]
        return render_template("lists/index.html", lists=lists)

class ListsCreate(MethodView):

    def get(self):
        return render_template("lists/create.html")

    def post(self):
        l = List()
        l.name = request.form['name']
        l.auth_url = request.form['auth_url']
        l.thanks_url = request.form['thanks_url']
        l.client = current_user.client
        l.save()
        return redirect(url_for('.index'))


lists.add_url_rule("/", view_func=ListsDefault.as_view('index'))
lists.add_url_rule("/create", view_func=ListsCreate.as_view('create'))
