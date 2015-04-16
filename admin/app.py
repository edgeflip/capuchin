import logging
import humongolus
from flask import Flask, redirect, url_for, request, g
from flask.ext.login import LoginManager, current_user
from flask.ext.session import Session
from flask_pjax import PJAX
from slugify import slugify

from admin import config
from capuchin import db
from capuchin.models.post import Post
from capuchin.util import date_format, to_json

from admin.models.user import User

logging.basicConfig(level=config.LOG_LEVEL)


def load_user(id):
    try:
        logging.debug("Loading User: %s", id)
        return User(id=id)
    except Exception as e:
        logging.exception(e)
        return None


class CapuchinAdmin(Flask):

    def __init__(self):
        super(CapuchinAdmin, self).__init__("admin")
        self.config.from_object('admin.config')
        logging.info("SERVER_NAME: {}".format(self.config['SERVER_NAME']))
        self.before_request(self.init_dbs)
        self.after_request(self.force_refresh)
        humongolus.settings(logging, db.init_mongodb())
        try:
            self.init_session()
            self.init_login()
            self.init_blueprints()
            self.init_pjax()
            self.init_templates()
            self.init_super_user()
        except Exception as e:
            logging.exception(e)

    def force_refresh(self, resp):
        resp.headers.extend({
            "Cache-Control": "no-store, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "Sat, 26 Jul 1997 05:00:00 GMT"
        })
        return resp

    def init_super_user(self):
        logging.info("Checking super user account...")
        su = User.find_one({'email':config.SUPER_USER_EMAIL})
        if not su:
            logging.info("Creating super user account")
            su = User()
            su.email = config.SUPER_USER_EMAIL
            su.password = config.SUPER_USER_PASSWORD
            su.name = "Super User"
            su.save()
        logging.info("Super User account created")

    def init_templates(self):
        self.jinja_env.filters['slugify'] = slugify
        self.jinja_env.filters['date_format'] = date_format
        self.jinja_env.filters['to_json'] = to_json

    def init_session(self):
        self.config['SESSION_MONGODB'] = db.init_mongodb()
        self.config['SESSION_MONGODB_DB'] = "capuchin_sessions"
        self.config['SESSION_MONGODB_COLLECT'] = "sessions"
        Session(self)

    def init_login(self):
        self.login_manager = LoginManager()
        self.login_manager.init_app(self)
        self.login_manager.user_callback = load_user
        self.login_manager.login_view = "auth.login"

    def user_logged_in(self):
        if not current_user.is_authenticated():
            return redirect(url_for("auth.login", next=request.path, _external=True))

    def init_pjax(self):
        PJAX(self)

    def configure_dbs(self):
        pass

    def init_dbs(self):
        g.ES = db.init_elasticsearch()
        g.INFLUX = db.init_influxdb()
        g.MONGO = db.init_mongodb()

    def init_blueprints(self):
        from controllers.auth import auth
        from controllers.clients import clients
        from controllers.frontend import frontend
        clients.before_request(self.user_logged_in)
        self.register_blueprint(auth)
        self.register_blueprint(clients)
        self.register_blueprint(frontend)
