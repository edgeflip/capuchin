from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask.ext.login import current_user
from flask.views import MethodView
from admin import config
from admin.util import email
from capuchin.models.client import Client
import logging

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

class ClientsCreate(MethodView):

    def get(self):
        return render_template("clients/create.html")

    def post(self):
        form = request.form
        org = form['org']
        temp_email = form['email']
        cl = Client()
        cl.name = org
        cl.admin_email_temp = temp_email
        try:
            cl.save()
            email.send(
                temp_email,
                'welcome',
                link='http://test.com/asdasda8s0d98a09s'
            )
            return redirect(url_for('clients.index'))
        except Exception as e:
            logging.exception(e)
            flash("Organization name already in use.", "danger")

        return render_template("clients/create.html")


clients.add_url_rule("/", view_func=ClientsDefault.as_view('index'))
clients.add_url_rule("/create", view_func=ClientsCreate.as_view('create'))
