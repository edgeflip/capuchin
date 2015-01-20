from flask import Flask
from elasticsearch import Elasticsearch
import config
import user_mapping

class Capuchin(Flask):

    def __init__(self):
        super(Capuchin, self).__init__("capuchin")
        self.es = Elasticsearch(hosts=config.ES_HOSTS)
        self.es.indices.create(
            index=config.ES_INDEX,
            body = {
                "settings":user_mapping.SETTINGS,
                "mappings":{
                    "users":{
                        "_source":{"enabled":True},
                        "properties":user_mapping.USER
                    }
                }
            },
            ignore=400
        )
