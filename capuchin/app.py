import logging

import humongolus
from flask import Flask, redirect, url_for, request, g
from flask.ext.login import LoginManager, current_user
from flask.ext.session import Session
from flask_pjax import PJAX
from slugify import slugify

from capuchin import config
from capuchin import db
from capuchin.models.client import Admin
from capuchin.models.post import Post
from capuchin.util import date_format, to_json
from capuchin.util.structs import LazySequence


logging.basicConfig(level=config.LOG_LEVEL)


def load_user(id):
    try:
        logging.debug("Loading User: %s", id)
        return Admin(id=id)
    except Exception as e:
        logging.exception(e)
        return None


def notification_context():
    if current_user.is_authenticated():
        try:
            posts = Post.records(client=current_user.client, sort=('created_time', 'desc'))
            segments = LazySequence(current_user.client.segments(query={"name": {"$ne": None}}))
        except:
            posts = ()
            segments = ()
    else:
        posts = segments = ()

    return {
        'notification': {
            'messages': config.MESSAGES,
            'posts': posts,
            'segments': segments,
        }
    }


class Capuchin(Flask):

    def __init__(self):
        super(Capuchin, self).__init__("capuchin")
        self.config.from_object('capuchin.config')
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
        except Exception as e:
            logging.exception(e)

    def force_refresh(self, resp):
        resp.headers.extend({
            "Cache-Control": "no-store, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "Sat, 26 Jul 1997 05:00:00 GMT"
        })
        return resp

    def init_templates(self):
        self.jinja_env.filters['slugify'] = slugify
        self.jinja_env.filters['date_format'] = date_format
        self.jinja_env.filters['to_json'] = to_json
        self.context_processor(notification_context)

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
        logging.debug(request.path)
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
        from controllers.dashboard import db
        from controllers.notifications import notifications
        from controllers.lists import lists
        from controllers.audience import audience
        from controllers.campaigns import campaigns
        from controllers.redirect import redirect
        from controllers.auth import auth
        from controllers.auth.facebook import facebook
        from controllers.healthcheck import hc
        from controllers.engagement import engagement
        from controllers.tables import tables
        from controllers.reports import reports

        db.before_request(self.user_logged_in)
        notifications.before_request(self.user_logged_in)
        lists.before_request(self.user_logged_in)
        audience.before_request(self.user_logged_in)
        campaigns.before_request(self.user_logged_in)
        engagement.before_request(self.user_logged_in)
        tables.before_request(self.user_logged_in)
        reports.before_request(self.user_logged_in)

        self.register_blueprint(hc)
        self.register_blueprint(db)
        self.register_blueprint(notifications)
        self.register_blueprint(lists)
        self.register_blueprint(audience)
        self.register_blueprint(campaigns)
        self.register_blueprint(redirect)
        self.register_blueprint(auth)
        self.register_blueprint(facebook)
        self.register_blueprint(engagement)
        self.register_blueprint(tables)
        self.register_blueprint(reports)
