from flask import current_app, url_for
from flask_login import current_user
from capuchin.models.user import User
from capuchin.models.segment import Segment
from capuchin.views.tables import Column, Table, MongoTable
from capuchin.util import date_format
import datetime
#TODO move all the html into templates and/or macros

def user_name(val, record):
    user_client = record.get_client(current_user.client)
    img = u"<img src=\"https://graph.facebook.com/v2.2/{}/picture?type=normal\" />".format(user_client.asid)
    return "<a data-toggle='tooltip' title='{}'>{} {}</a>".format(img, record.first_name, record.last_name)

def user_notification(val, record):
    return date_format(record.get("last_notification", "NA"))

def user_location(v, r):
    return r.location_name.location

user_columns = [
    Column('first_name', "Name", formatter=user_name, sortable=True),
    Column('age', "Age", sortable=True),
    Column('gender', "Gender", sortable=True),
    Column('location_name.city', "Location", formatter=user_location),
    Column('', "Source", formatter=lambda v, r: "Facebook Ad"),
    Column('last_notification', "Last Notification", formatter=user_notification, sortable=True),
    #Column('', 'Link', formatter=lambda v,r: "Action", cls="actions"),
]

class Users(Table):
    cls = User
    columns = user_columns


class SegmentUsers(Users):

    def get_records(self, q, from_, size, sort):
        segment = Segment(id=self.obj)
        records = segment.records(q, from_, size, sort)
        total = records.total
        return records, total


def segment_count(v, r):
    return "{:,}".format(r.count)

def segment_actions(v, r):
    return "<div class=\"btn-group btn-group-xs\">\
        <a class='btn btn-primary' href=\"{}\" role=\"button\">Grow</a>\
        <a class=\"btn btn-primary\" href=\"{}\" role=\"button\">Engage</a>\
    </div>".format(
        url_for('notifications.create', segment=str(r._id)),
        url_for('notifications.create', segment=str(r._id), engage=1)
    )

def date_formatter(v, r):
    return date_format(v)

segment_columns = [
    Column('name', "Name", sortable=True),
    Column('created', "Created", formatter=date_formatter, sortable=True),
    Column('', 'Members', formatter=segment_count),
    Column('', 'Engagement', formatter=lambda r,v: "...", sortable=True),
    Column('last_notification', "Last Notification", formatter=date_formatter, sortable=True),
    Column('', 'Actions', formatter=segment_actions),
]

class Segments(MongoTable):
    cls = Segment
    columns = segment_columns
