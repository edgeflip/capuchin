from flask import Flask, redirect, url_for, request, g
from flask_pjax import PJAX
from flask.ext.login import LoginManager, current_user
from flask.ext.session import Session
from capuchin.models.client import Admin
from capuchin import db
from elasticsearch import TransportError
from slugify import slugify
import humongolus
from capuchin import config
import logging
import time
import gevent

logging.basicConfig(level=config.LOG_LEVEL)

class Capuchin(Flask):

    def __init__(self):
        super(Capuchin, self).__init__("capuchin")
        self.config.from_object('capuchin.config')
        logging.info("SERVER_NAME: {}".format(self.config['SERVER_NAME']))
        self.before_request(self.init_dbs)
        humongolus.settings(logging, db.init_mongodb())
        try:
            self.init_session()
            self.init_login()
            self.init_blueprints()
            self.init_pjax()
            self.init_templates()
        except Exception as e:
            logging.exception(e)

    def load_user(self, id):
        try:
            logging.info("Loading User: {}".format(id))
            a = Admin(id=id)
            return a
        except Exception as e:
            logging.exception(e)
            return None

    def init_templates(self):
        self.jinja_env.filters['slugify'] = slugify

    def init_session(self):
        self.config['SESSION_MONGODB'] = db.init_mongodb()
        self.config['SESSION_MONGODB_DB'] = "capuchin_sessions"
        self.config['SESSION_MONGODB_COLLECT'] = "sessions"
        Session(self)

    def init_login(self):
        self.login_manager = LoginManager()
        self.login_manager.init_app(self)
        self.login_manager.user_callback = self.load_user
        self.login_manager.login_view = "auth.login"

    def user_logged_in(self):
        logging.info(request.path)
        if not current_user.is_authenticated():
            return redirect(url_for("auth.login", next=request.path, _external=True))

    def init_pjax(self):
        PJAX(self)

    def configure_dbs(self):pass

    def init_dbs(self):
        g.ES = db.init_elasticsearch()
        g.INFLUX = db.init_influxdb()
        g.MONGO = db.init_mongodb()

    def init_blueprints(self):
        from controllers.dashboard import db
        from controllers.notifications import notif
        from controllers.lists import lists
        from controllers.audience import audience
        from controllers.campaigns import campaigns
        from controllers.redirect import redirect
        from controllers.auth import auth
        from controllers.auth.facebook import facebook
        from controllers.healthcheck import hc
        from controllers.posts import posts
        db.before_request(self.user_logged_in)
        notif.before_request(self.user_logged_in)
        lists.before_request(self.user_logged_in)
        audience.before_request(self.user_logged_in)
        campaigns.before_request(self.user_logged_in)
        posts.before_request(self.user_logged_in)
        self.register_blueprint(hc)
        self.register_blueprint(db)
        self.register_blueprint(notif)
        self.register_blueprint(lists)
        self.register_blueprint(audience)
        self.register_blueprint(campaigns)
        self.register_blueprint(redirect)
        self.register_blueprint(auth)
        self.register_blueprint(facebook)
        self.register_blueprint(posts)
