SETTINGS = {
    "index": {
        "analysis": {
            "analyzer": {
                "lowercase": {
                    "tokenizer": "keyword",
                    "filter": "lowercase"
                },
                "title_stemming": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "snowball"]
                },
                "autocomplete":{
                    "type":"custom",
                    "tokenizer":"standard",
                    "filter":[ "standard", "lowercase", "stop", "kstem", "ngram" ]
                },
                "autocomplete_multiword":{
                    "type":"custom",
                    "tokenizer": "keyword",
                    "filter":[ "standard", "lowercase", "stop", "kstem", "edge_ngram" ],
                },
            },
            "filter": {
                "ngram": {
                    "type": "nGram",
                    "min_gram": 2,
                    "max_gram": 8,
                },
                "edge_ngram": {
                    "type": "edgeNGram",
                    "min_gram": 2,
                    "max_gram": 12,
                },
                "snowball": {
                    "type": "snowball",
                    "language": "English"
                }
            },
        }
    }
}

POST = {
    "client":{
        "type":"string",
        "index": "not_analyzed"
    }
}

NOTIFICATION = {
    "client":{
        "type":"string",
        "index": "not_analyzed"
    }
}

SEGMENT = {
    "client":{
        "type":"string",
        "index": "not_analyzed"
    }
}

USER = {
    "efid": {"type": "long",},
    "clients":{
        "properties":{
            "asid":{"type":"string", "index":"not_analyzed"},
            "id":{"type":"string", "index":"not_analyzed"},
            "source":{"type":"string", "index":"not_analyzed"},
            "import_origins":{"type":"string", "index":"not_analyzed"},
            "engagement": {"type": "integer"},
            "authed":{"type":"date"},
        }
    },
    # from v2_users
    "first_name": {"type": "string",},
    "last_name": {"type": "string",},
    "interests": {"type":"string", "index":"not_analyzed"},
    "location_name":{
        "properties":{
            "location":{
                "type": "multi_field",
                "fields":{
                    "facet":{
                        "type":"string",
                        "index": "not_analyzed"
                    },
                    "suggest": {
                        "type": "string",
                        "analyzer": "autocomplete"
                    },
                    "search": {
                        "type": "string"
                    }
                }
            },
            "city": {
                "type": "multi_field",
                "fields":{
                    "facet":{
                        "type":"string",
                        "index": "not_analyzed"
                    },
                    "suggest": {
                        "type": "string",
                        "analyzer": "autocomplete_multiword"
                    }
                }
            },
            "state": {
                "type": "multi_field",
                "fields":{
                    "facet":{
                        "type":"string",
                        "index": "not_analyzed"
                    },
                    "suggest": {
                        "type": "string",
                        "analyzer": "autocomplete"
                    }
                }
            },
        }
    },
    "locale":{
        "type": "multi_field",
        "fields": {
            "search": {
                "type": "string"
            },
            "facet": {
                "type": "string",
                "index": "not_analyzed",
            },
            "suggest": {
                "type": "string",
                "analyzer": "autocomplete"
            }
        }
    },
    "birthday": {"type": "date",},
    "gender": {"type": "string", "index": "not_analyzed",},
    "timezone": {"type": "integer",},
    "locale": {"type": "string",},
    # v2_user_aggregates
    "age":{"type": "integer",},
    "last_activity": {"type": "date",},
    "first_activity": {"type": "date",},
    "num_taggable_friends":{"type": "integer",},
    "num_person_edges":{"type": "integer",},
    "num_posts":{"type": "integer",},
    "num_posts_with_edges":{"type": "integer",},
    "num_posts_liked":{"type": "integer",},
    "num_posts_commented_on":{"type": "integer",},
    "num_posts_shared":{"type": "integer",},
    "num_stat_updates":{"type": "integer",},
    "num_post_interactors":{"type": "integer",},
    "avg_days_between_activity":{"type": "float"},
    "avg_post_interactors":{"type": "float"},
    "affiliations": {
        "properties":{
            "category": {"type": "string", "index": "not_analyzed"},
            "name": {
                "type": "multi_field",
                "fields": {
                    "search": {
                        "type": "string"
                    },
                    "facet": {
                        "type": "string",
                        "index": "not_analyzed",
                    },
                    "suggest": {
                        "type": "string",
                        "analyzer": "autocomplete"
                    }
                }
            }
        }
    },
    "languages": {
        "properties":{
            "language": {
                "type": "multi_field",
                "fields": {
                    "search": {
                        "type": "string"
                    },
                    "facet": {
                        "type": "string",
                        "index": "not_analyzed",
                    },
                    "suggest": {
                        "type": "string",
                        "analyzer": "autocomplete"
                    }
                }
            }
        }
    },
    "likes": {
        "properties":{
            "fb_category": {"type": "string", "index": "not_analyzed"},
            "ef_categories": {
                "properties": {
                    "name": {"type": "string", "index": "not_analyzed"},
                },
            },
            "name": {
                "type": "multi_field",
                "fields": {
                    "search": {
                        "type": "string"
                    },
                    "facet": {
                        "type": "string",
                        "index": "not_analyzed",
                    },
                    "suggest": {
                        "type": "string",
                        "analyzer": "autocomplete"
                    }
                }
            }
        }
    },
    "permissions": {
        "properties":{
            "permission": {"type": "string", "index": "not_analyzed"},
            "status": {"type": "string", "index": "not_analyzed"},
        }
    },
    "email": {
        "properties":{
            "email":{"type":"string"},
            "handle":{
                "type":"string"
            },
            "domain":{
                "type": "multi_field",
                "fields": {
                    "search": {
                        "type": "string"
                    },
                    "facet": {
                        "index": "not_analyzed",
                        "type": "string",
                    },
                    "suggest": {
                        "type": "string",
                        "analyzer": "autocomplete"
                    }
                }
            }
        }
    },
 }
