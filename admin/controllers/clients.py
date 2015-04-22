from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask.ext.login import current_user
from flask.views import MethodView
from admin import config
from admin.util import email
from capuchin.models.client import Client, Admin, AccountToken
from capuchin.util import magnus
import logging

clients = Blueprint(
    'clients',
    __name__,
    template_folder=config.TEMPLATES,
    url_prefix="/clients",
)

def create_client(name, email):
    cl = Client()
    cl.name = name
    cl.save()
    magnus.get_or_create_magnus_client(cl.slug, name)
    admin = Admin()
    admin.email = email
    admin.password = cl._id
    admin.client = cl
    admin.save()
    at = AccountToken()
    at.admin = admin
    at.save()
    return at._id

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
        em = form['email']
        token = create_client(org, em)
        nex = url_for('frontend.facebook_login')
        try:
            email.send(
                em,
                'welcome',
                link=url_for('frontend.token', token=token, next=nex, _external=True)
            )
            return redirect(url_for('clients.index'))
        except Exception as e:
            logging.exception(e)
            flash(e.message, "danger")

        return render_template("clients/create.html")


clients.add_url_rule("/", view_func=ClientsDefault.as_view('index'))
clients.add_url_rule("/create", view_func=ClientsCreate.as_view('create'))
