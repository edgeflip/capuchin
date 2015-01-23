SETTINGS = {
    "index": {
        "analysis": {
            "analyzer": {
                "kw_analyzer": {
                    "type": "custom",
                    "tokenizer": "lowercase",
                    "filter": ["kw_ngram"]
                },
                "lowercase": {
                    "tokenizer": "keyword",
                    "filter": "lowercase"
                },
                "title_stemming": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "snowball"]
                }
            },
            "filter": {
                "kw_ngram": {
                    "type": "nGram",
                    "min_gram": 2,
                    "max_gram": 20,
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
    "city": {"type": "string", "index": "not_analyzed",},
    "state": {"type": "string", "index": "not_analyzed",},
    "country": {"type": "string", "index": "not_analyzed",},
    "updated": {"type": "date",},
    "profile_update_time":{"type": "date"},
    "quotes": {"type": "string",},
    "religion": {"type": "string",},
    "birthday": {"type": "date",},
    "gender": {"type": "string", "index": "not_analyzed",},
    "music": {"type": "string", "index": "not_analyzed",},
    "political": {"type": "string", "index": "not_analyzed",},
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
        "type":"string",
        "index":"not_analyzed",
    },
    "affiliations": {
        "properties":{
            "type": {"type": "string", "index": "not_analyzed"},
            "name": {"type": "string", "index": "not_analyzed"},
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
                        "type": "string",
                    },
                    "facet": {
                        "type": "string",
                        "index": "not_analyzed",
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
                "type":"multi_field",
                "fields":{
                    "search":{
                        "type":"string",

                    },
                    "facet":{
                        "type":"string",
                        "index":"not_analyzed"
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
            }
        }
    },
 }
