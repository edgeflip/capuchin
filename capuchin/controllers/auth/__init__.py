from flask import Blueprint, render_template, flash, request, redirect, url_for, session
from flask.ext.login import login_user, current_user
from flask.views import MethodView
from capuchin import config
from capuchin.models.client import Client, Admin
import logging

auth = Blueprint(
    'auth',
    __name__,
    template_folder=config.TEMPLATES,
    subdomain=config.AUTH_SUBDOMAIN,
)

class AuthLogin(MethodView):

    def get(self):
        return render_template("auth/login.html")

    def post(self):
        form = request.form
        em = form['email']
        pw = form['password']
        a = Admin.find_one({'email':em})
        if a and a.verify_pwd(pw):
            success = login_user(a)
            logging.info("LOGGED IN: {}".format(success))
            return redirect(url_for("dashboard.index"))
        else:
            flash("Please try again")

        return render_template("auth/login.html", form=form)

class AuthRegister(MethodView):

    def get(self):
        return render_template("auth/register.html")

    def post(self):
        form = request.form
        pwd = form['password']
        logging.info(pwd)
        cpwd = form['confirm_password']
        if not Admin.passwords_match(pwd, cpwd):
            logging.info(cpwd)
            flash("Passwords do not match")
            return render_template("auth/register", form=form)

        cl = Client()
        cl.name = form['org']
        cl.save()
        logging.info(cl)
        a = Admin()
        a.name = form['name']
        a.email = form['email']
        a.password = form['password']
        a.client = cl
        a.save()
        login_user(a)
        return redirect(url_for("dashboard.index", first=True))

auth.add_url_rule("/login", view_func=AuthLogin.as_view('login'))
auth.add_url_rule("/register", view_func=AuthRegister.as_view('register'))
