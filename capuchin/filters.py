FILTERS = [
    {
        "display":"Location",
        "field":"location_name.location",
        "type":"term",
        "aggregation_args":{}
    },
    {
        "display":"Age",
        "field":"age",
        "type":"range",
        "aggregation_args":{
            "interval":10,
            "min_doc_count":0,
            "interval":1,
        }
    },
    {
        "display":"Gender",
        "field":"gender",
        "type":"gender",
        "aggregation_args":{}
    },
    {
        "display":"Affiliations",
        "field":"affiliations.name",
        "type":"term",
        "aggregation_args":{}
    },
    {
        "display":"Popularity",
        "field":"num_people_interacted_with_my_posts",
        "type":"range",
        "aggregation_args":{
            "interval" : 100,
            "min_doc_count": 100,
            "extended_bounds" : {
                "min" : 100,
                "max" : 5000
            }
        }
    },
]

def range_filter(field, value):
    return {
        "range":{
            field:{
                "from":value[0],
                "to": value[1]
            }
        }
    }

def term_filter(field, value):
    return {
        "term":{
            "{}.facet".format(field):value
        }
    }

def term_list_filter(field, value):
    return {
        "term":{
            field:value
        }
    }

FILTER_TYPES = {
    "range": range_filter,
    "term": term_filter,
    "term_list": term_list_filter,
}

def get_filter(filters, field):
    for f in filters:
        if f['field'] == field: return f
