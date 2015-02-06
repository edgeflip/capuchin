from flask import Flask, redirect, url_for, request
from flask_pjax import PJAX
from flask.ext.login import LoginManager, current_user
from flask.ext.session import Session
from pymongo import MongoClient
from elasticsearch import Elasticsearch
from capuchin.models.client import Admin
from elasticsearch import TransportError
from capuchin import influx
import influxdb
import humongolus
import config
import user_mapping
import logging
import time
import gevent

logging.basicConfig(level=config.LOG_LEVEL)
es_connected = False

while not es_connected:
    try:
        gevent.sleep(1)
        ES = Elasticsearch(hosts=config.ES_HOSTS, sniff_on_start=True, sniff_on_connection_fail=True, sniffer_timeout=60)
        es_connected = True
    except TransportError as e:
        logging.exception(e)

MONGO = MongoClient(config.MONGO_HOST, config.MONGO_PORT)
INFLUX = influxdb.InfluxDBClient(
    config.INFLUX_HOST,
    config.INFLUX_PORT,
    config.INFLUX_USER,
    config.INFLUX_PASSWORD,
    config.INFLUX_DATABASE
)


def create_index():
    ES.indices.create(
        index=config.ES_INDEX,
        body = {
            "settings":user_mapping.SETTINGS,
            "mappings":{
                "user":{
                    "_source":{"enabled":True},
                    "properties":user_mapping.USER
                }
            }
        },
        ignore=400
    )

class Capuchin(Flask):

    def __init__(self):
        super(Capuchin, self).__init__("capuchin")
        self.config.from_object('capuchin.config')
        if not ES.indices.exists(config.ES_INDEX):
            create_index()
        humongolus.settings(logging, MONGO)

        try:
            self.init_session()
            self.init_login()
            self.init_blueprints()
            self.init_influx()
            self.init_pjax()
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

    def init_session(self):
        self.config['SESSION_MONGODB'] = MONGO
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

    def init_influx(self):
        data = {
            "name":config.INFLUX_DATABASE,
            "spaces":influx.SPACES,
            "continuousQueries":influx.QUERIES,
        }
        try:
            res = INFLUX.request(
                url="cluster/database_configs/{}".format(config.INFLUX_DATABASE),
                data=data,
                method="POST"
            )
            logging.debug(res)
        except Exception as e:
            logging.warning(e)

    def init_blueprints(self):
        from controllers.dashboard import db
        from controllers.notifications import notif
        from controllers.lists import lists
        from controllers.segments import segments
        from controllers.campaigns import campaigns
        from controllers.redirect import redirect
        from controllers.auth import auth
        from controllers.auth.facebook import facebook
        db.before_request(self.user_logged_in)
        notif.before_request(self.user_logged_in)
        lists.before_request(self.user_logged_in)
        segments.before_request(self.user_logged_in)
        campaigns.before_request(self.user_logged_in)
        self.register_blueprint(db)
        self.register_blueprint(notif)
        self.register_blueprint(lists)
        self.register_blueprint(segments)
        self.register_blueprint(campaigns)
        self.register_blueprint(redirect)
        self.register_blueprint(auth)
        self.register_blueprint(facebook)
