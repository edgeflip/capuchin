from flask import Blueprint, render_template, request, redirect, url_for
from flask.views import MethodView
from capuchin import config
from capuchin.models.list import List

redirect = Blueprint(
    'redirect',
    __name__,
    template_folder=config.TEMPLATES,
    url_prefix="/redirect",
)

class RedirectList(MethodView):

    def get(self, id):
        l = List(id=id)
        return redirect(l.auth_url)

redirect.add_url_rule("/list/<id>", view_func=RedirectList.as_view('list'))
