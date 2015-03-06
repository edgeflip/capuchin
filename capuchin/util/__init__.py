import logging
import datetime
import json
from jinja2 import Markup
formats = [
    "%Y-%m-%dT%H:%M:%S+0000",
    "%Y-%m-%dT%H:%M:%S.%f",
]


def date_format(date, format="%m/%d/%Y", default="NA"):
    for i in formats:
        try:
            date = datetime.datetime.strptime(date, i)
            break
        except: pass

    try:
        return date.strftime(format)
    except Exception as e:
        #logging.exception(e)
        return default


def to_json(val):
    return Markup(json.dumps(val))
