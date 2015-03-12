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
        "field":"engagement",
        "type":"engagement",
        "icon":"icon-bubbles",
        "aggregation_args":{},
    },
    {
        "display":"Joined",
        "field":"joined",
        "type":"joined",
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
        "field":"lists",
        "type":"lists",
        "icon":"icon-list",
        "aggregation_args":{}
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

def age_filter(field, value):
    obj = range_filter(field, value)
    if value[1] == 65:
        del obj['range'][field]['to']
        obj['range'][field]['gte'] = value[1]
    else:
        obj['range'][field]['to'] = value[1]

    return obj

FILTER_TYPES = {
    "range": range_filter,
    "term": term_filter,
    "term_list": term_list_filter,
    "age": age_filter,
    "joined": range_filter,
    "interests": term_filter,
    "engagement": range_filter,
    "lists": term_filter,
    "gender": term_list_filter,
}

def get_filter(filters, field):
    for f in filters:
        if f['field'] == field: return f
