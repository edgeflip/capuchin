from flask import Flask
from elasticsearch import Elasticsearch
import config
import user_mapping
import logging

class Capuchin(Flask):

    def __init__(self):
        super(Capuchin, self).__init__("capuchin")
        self.es = Elasticsearch(hosts=config.ES_HOSTS)
        self.es.indices.create(
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
        self.init_blueprints()

    def init_blueprints(self):
        logging.debug("registering blueprints")
        from controllers.dashboard import db
        from controllers.notifications import notif
        from controllers.lists import lists
        self.register_blueprint(db)
        self.register_blueprint(notif)
        self.register_blueprint(lists)
