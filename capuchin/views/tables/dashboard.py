from flask import current_app, url_for
from capuchin.models.post import Post
from capuchin.models.notification import Notification
from capuchin.util import date_format
from capuchin.views.tables import Column, Table, MongoTable
import random
import logging

#TODO move all the html into templates and/or macros

def post_type(val, record):
    try:
        return "<img src=\"{}\" />".format(record.icon)
    except:
        return ""

def post_targeting(val, record):
    return """<span class="icon-globe"></span>"""

def post_engagement(val, record):
    return "<p>{}</p><p>{}</p>".format(len(record.comments), len(record.likes))

def post_actions(val, record):
    return """<div class="btn-group btn-group-xs" role="group" aria-label="...">
            <a href="{}" class="btn btn-default">View</button>
            <a href="{}" class="btn btn-default">Boost</button>
        </div>""".format(
            url_for('engagement.view', id=record.id),
            url_for('notifications.create', post=record.id, engage=1)
        )

def post_message(val, record):
    logging.info(val)
    try:
        img = "<div class=\"col-md-2\"><img class=\"table-image\" src=\"{}\" /></div>".format(record.picture)
    except:
        img = "<div class=\"col-md-2\"></div>"
    truncated_val = current_app.jinja_env.filters['truncate'](val, 120)
    logging.info(truncated_val)
    mes = u"<div class=\"col-md-10\"><p>{}</p></div>".format(truncated_val)
    return u"{}{}".format(img, mes)

def date_formatter(v, r):
    return date_format(r.created_time)

post_columns = [
    Column('created_time', "Published", formatter=date_formatter, sortable=True),
    Column('message', "Post", formatter=post_message, sortable=True),
    Column('', "Type", formatter=post_type),
    Column('', "Targeting", formatter=post_targeting),
    Column('', "Reach", formatter=lambda v, r: "1,090"),
    Column('', "Engagment", formatter=post_engagement),
    Column('', '', formatter=post_actions, cls="actions"),
]

class Posts(Table):
    cls = Post
    columns = post_columns

def notif_message(v, r):
    return current_app.jinja_env.filters['truncate'](v, 25)

notification_columns = [
    Column('created', 'Date', formatter=lambda v, r: date_format(v)),
    Column('', 'Notification', formatter=lambda v,r: 'Notification'),
    Column('', 'Segment', formatter=lambda v,r: r.segment.name),
    Column('message', 'Description', formatter=notif_message),
    Column('engagement', 'Click %', formatter=lambda v, r: "{}%".format(random.randint(2, 99)))
]

class Notifications(MongoTable):
    cls = Notification
    columns = notification_columns
