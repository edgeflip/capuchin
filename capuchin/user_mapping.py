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
            },
            "filter": {
                "ngram": {
                    "type": "nGram",
                    "min_gram": 2,
                    "max_gram": 8,
                },
                "snowball": {
                    "type": "snowball",
                    "language": "English"
                }
            },
        }
    }
}

USER = {
    "fbid": {"type": "long",},
    "fname": {"type": "string",},
    "lname": {"type": "string",},
    "city": {
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
    "country":{
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
    "updated": {"type": "date",},
    "profile_update_time":{"type": "date"},
    "quotes": {"type": "string",},
    "religion": {
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
    "birthday": {"type": "date",},
    "gender": {"type": "string", "index": "not_analyzed",},
    "music": {
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
    "political": {
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
    "relationship_status": {"type": "string", "index": "not_analyzed",},
    "likes_count": {"type": "integer",},
    "wall_count": {"type": "integer", "index": "not_analyzed",},
    "friend_request_count": {"type": "integer",},
    "age":{"type": "integer",},
    "first_activity": {"type": "date",},
    "last_activity":{"type": "date",},
    "num_friends":{"type": "integer",},
    "num_posts":{"type": "integer",},
    "num_posts_interacted_with":{"type": "integer"},
    "num_i_like":{"type": "integer",},
    "num_i_comm":{"type": "integer",},
    "num_shared_w_me":{"type": "integer",},
    "num_mine_liked":{"type": "integer",},
    "num_mine_commented":{"type": "integer",},
    "num_i_shared":{"type": "integer",},
    "num_stat_upd":{"type": "integer",},
    "num_friends_interacted_with_my_posts":{"type": "integer"},
    "num_friends_i_interacted_with":{"type": "integer"},
    "avg_time_between_activity":{"type": "integer"},
    "avg_friends_interacted_with_my_posts":{"type": "integer"},
    "avg_friends_i_interacted_with":{"type": "integer"},
    "top_words":{
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
    "affiliations": {
        "properties":{
            "type": {"type": "string", "index": "not_analyzed"},
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
    "devices": {
        "properties":{
            "hardware": {"type": "string", "index": "not_analyzed"},
            "os": {"type": "string", "index": "not_analyzed"},
        }
    },
    "books": {
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
    "tv": {
        "type": "multi_field",
        "fields": {
            "search": {
                "type": "string",
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
    "sports":{
        "properties":{
            "name":{
                "type": "multi_field",
                "fields": {
                    "search": {
                        "type": "string",
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
            "name":{
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
    "interests": {
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
    "movies": {
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
 }
