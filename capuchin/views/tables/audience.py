from flask import current_app, url_for
from flask_login import current_user
from capuchin.models.user import User
from capuchin.models.segment import Segment
from capuchin.views.tables import Column, Table, MongoTable
from capuchin.util import date_format
import datetime
#TODO move all the html into templates and/or macros

def user_name(val, record):
    return u"{} {}".format(record.first_name, record.last_name)

def user_notification(val, record):
    return date_format(record.get("last_notification", "NA"))

def user_location(v, r):
    return r.location.location

user_columns = [
    Column('first_name', "Name", formatter=user_name, sortable=True),
    Column('age', "Age", sortable=True),
    Column('gender', "Gender", sortable=True),
    Column('location.city', "Location", formatter=user_location),
    Column('', "Source", formatter=lambda v, r: "Facebook Ad"),
    Column('last_notification', "Last Notification", formatter=user_notification),
    Column('', 'Link', formatter=lambda v,r: "Action", cls="actions"),
]

class Users(Table):
    cls = User
    columns = user_columns


def segment_count(v, r):
    return "{:,}".format(r.count)

def segment_actions(v, r):
    return "<a class='btn btn-primary' href=\"{}\" role=\"button\">View</a>".format(url_for('audience.id', id=str(r._id)))

def date_formatter(v, r):
    return date_format(v)

segment_columns = [
    Column('name', "Name", sortable=True),
    Column('created', "Created", formatter=date_formatter),
    Column('', 'Members', formatter=segment_count),
    Column('', 'Engagement', formatter=lambda r,v: "..."),
    Column('last_notification', "Last Notification", formatter=date_formatter),
    Column('', 'Actions', formatter=segment_actions),
]

class Segments(MongoTable):
    cls = Segment
    columns = segment_columns
