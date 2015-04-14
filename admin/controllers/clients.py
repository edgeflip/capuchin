from flask import Blueprint, render_template, request, redirect, url_for
from flask.ext.login import current_user
from flask.views import MethodView
from admin import config
from capuchin.models.client import Client

clients = Blueprint(
    'clients',
    __name__,
    template_folder=config.TEMPLATES,
    url_prefix="/clients",
)

class ClientsDefault(MethodView):

    def get(self):
        clients = [l for l in Client.find()]
        return render_template("clients/index.html", clients=clients)

clients.add_url_rule("/", view_func=ClientsDefault.as_view('index'))
