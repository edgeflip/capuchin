from flask import Blueprint, render_template, flash, request, redirect, url_for, session, get_flashed_messages
from flask.ext.login import login_user, current_user, logout_user
from flask.views import MethodView
from pymongo.errors import DuplicateKeyError
from capuchin import config
from capuchin.integration import magnus
from capuchin.models.client import Client, Admin, Competitor, AccountToken
from capuchin.util import password
import logging

auth = Blueprint(
    'auth',
    __name__,
    template_folder=config.TEMPLATES,
    url_prefix="/auth",
)

class AuthToken(MethodView):

    def get(self, token):
        nex = request.args.get('next')
        token = AccountToken(id=token)
        success = login_user(token.admin)
        nex = nex if nex else url_for('dashboard.index')
        return redirect(nex)

class AuthPassword(MethodView):

    def get(self):
        return render_template("auth/password.html")

    def post(self):
        form = request.form
        pwd = form['password']
        cpwd = form['confirm_password']
        if not Admin.passwords_match(pwd, cpwd):
            flash("Passwords do not match", "danger")
            return render_template("auth/password.html", form=form)

        a = Admin(id=current_user._id)
        a.password = pwd
        a.save()
        return redirect(url_for('dashboard.index'))


class AuthLogin(MethodView):

    def get(self):
        return render_template("auth/login.html")

    def post(self):
        form = request.form
        em = form['email']
        pw = form['password']
        a = Admin.find_one({'email':em})
        if a and a.verify_pwd(pw):
            rem = False
            if form.get("remember-me"): rem = True
            success = login_user(a, remember=rem)
            return redirect(url_for("dashboard.index"))
        else:
            flash("Invalid Credentials", "danger")

        return render_template("auth/login.html", form=form)

class AuthRegister(MethodView):

    def get(self):
        return render_template("auth/register.html")

    def post(self):
        form = request.form
        pwd = form['password']
        cpwd = form['confirm_password']
        if not Admin.passwords_match(pwd, cpwd):
            flash("Passwords do not match", "danger")
            return render_template("auth/register.html", form=form)
        try:
            cl = Client()
            cl.name = form['org']
            cl.slug = cl.name
            cl.save()
        except DuplicateKeyError as e:
            logging.exception(e)
            flash("Organization name already taken", "danger");
            return render_template("auth/register.html", form=form)
        magnus.get_or_create_client(cl.slug, cl.name)
        try:
            a = Admin()
            a.name = form['name']
            a.email = form['email']
            a.password = form['password']
            a.client = cl
            a.save()
        except DuplicateKeyError as e:
            logging.exception(e)
            flash("Email address already taken", "danger");
            return render_template("auth/register.html", form=form)

        login_user(a)
        return redirect(url_for("facebook.index"))


class AuthLogout(MethodView):

    def get(self):
        logout_user()
        return redirect(url_for(".login"))

auth.add_url_rule("/login", view_func=AuthLogin.as_view('login'))
auth.add_url_rule("/logout", view_func=AuthLogout.as_view('logout'))
auth.add_url_rule("/register", view_func=AuthRegister.as_view('register'))
auth.add_url_rule("/token/<token>", view_func=AuthToken.as_view('token'))
auth.add_url_rule("/password", view_func=AuthPassword.as_view('password'))
