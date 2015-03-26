import datetime
import logging

FILTERS = [
    {
        "display":"City",
        "field":"location_name.city",
        "type":"term",
        "aggregation_args":{},
        "icon":"icon-pointer"
    },
    {
        "display":"State",
        "field":"location_name.state",
        "type":"term",
        "aggregation_args":{},
        "icon":"icon-pointer"
    },
    {
        "display":"Age",
        "field":"age",
        "type":"age",
        "icon":"icon-eyeglasses",
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
        "icon":"icon-users",
        "aggregation_args":{}
    },
    {
        "display":"Interests",
        "field":"interests",
        "type":"interests",
        "icon":"icon-flag",
        "aggregation_args":{}
    },
    {
        "display":"Engagement",
        "field":"clients.engagement",
        "type":"engagement",
        "icon":"icon-bubbles",
        "aggregation_args":{},
    },
    {
        "display":"Joined",
        "field":"first_activity",
        "type":"first_activity",
        "icon":" icon-like",
        "aggregation_args":{}
    },
    {
        "display":"Affiliations",
        "field":"affiliations.name",
        "type":"term",
        "aggregation_args":{}
    },
    {
        "display":"Link to List",
        "field":"clients.import_origins",
        "type":"import_origins",
        "icon":"icon-list",
        "aggregation_args":{}
    },
]

def range_filter(field, value, **kwargs):
    return {
        "range":{
            field:{
                "gte":value[0],
                "lte": value[1]
            }
        }
    }

def term_filter(field, value, **kwargs):
    if isinstance(value, list):
        return {
            "bool":{
                "should":[{'term':{'{}.facet'.format(field): v}} for v in value]
            }
        }
    return {
        "term":{
            "{}.facet".format(field):value
        }
    }

def interests_filter(field, value, **kwargs):
    return {
        "term":{
            "{}".format(field):value
        }
    }

def term_list_filter(field, value, **kwargs):
    return {
        "term":{
            field:value
        }
    }

def age_filter(field, value, **kwargs):
    obj = range_filter(field, value)
    if value[1] == 65: obj['range'][field]['lte'] = 200

    return obj

def qualifier_filter(field, value, **kwargs):
    if value.get("qualifier") == 'eq':
        return {
            "range":{
                field:{
                    'gte':value.get("value"),
                    'lte':value.get("value"),
                }
            }
        }

    return {
        "range":{
            field:{
                value.get("qualifier"):value.get("value")
            }
        }
    }

def date_qualifier_filter(field, value, **kwargs):
    value['value'] = datetime.datetime.strptime(value['value'], "%m/%d/%Y")
    return qualifier_filter(field, value, **kwargs)

def client_qualifier_filter(field, value, **kwargs):
    obj = qualifier_filter(field, value, **kwargs)
    return {
        "and":[
            obj,
            {"term":{"clients.id":kwargs.get('client')}}
        ]

    }

def client_term_filter(field, value, **kwargs):
    obj = term_filter(field, value, **kwargs)
    return {
        "and":[
            {"term":{field:value}},
            {"term":{"clients.id":kwargs.get('client')}}
        ]
    }

def gender_list_filter(field, value, **kwargs):
    if value == 'all': return None
    return term_list_filter(field, value, **kwargs)

FILTER_TYPES = {
    "range": range_filter,
    "term": term_filter,
    "term_list": term_list_filter,
    "age": age_filter,
    "first_activity": date_qualifier_filter,
    "interests": interests_filter,
    "engagement": client_qualifier_filter,
    "import_origins": client_term_filter,
    "gender": gender_list_filter,
}

def get_filter(filters, field):
    for f in filters:
        if f['field'] == field: return f
