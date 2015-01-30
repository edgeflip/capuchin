from flask import Flask
from pymongo import MongoClient
from elasticsearch import Elasticsearch
import humongolus
import config
import user_mapping
import logging

ES = Elasticsearch(hosts=config.ES_HOSTS)
MONGO = MongoClient(config.MONGO_HOST, config.MONGO_PORT)

class Capuchin(Flask):

    def __init__(self):
        super(Capuchin, self).__init__("capuchin")
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
        humongolus.settings(logging, MONGO)

        try:
            self.init_blueprints()
        except Exception as e:
            logging.exception(e)

    def init_blueprints(self):
        logging.debug("registering blueprints")
        from controllers.dashboard import db
        from controllers.notifications import notif
        from controllers.lists import lists
        from controllers.segments import segments
        from controllers.campaigns import campaigns
        self.register_blueprint(db)
        self.register_blueprint(notif)
        self.register_blueprint(lists)
        self.register_blueprint(segments)
        self.register_blueprint(campaigns)
