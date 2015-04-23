import logging
import random

from flask import current_app, url_for

from capuchin.models.notification import NotificationSearch
from capuchin.models.segment import SegmentSearch
from capuchin.models.post import Post
from capuchin.util import date_format
from capuchin.views.tables import Column, Table



def notif_message(v, r):
    return current_app.jinja_env.filters['truncate'](v, 25)

notification_columns = [
    Column('created', 'Date', formatter=lambda v, r: date_format(v)),
    Column('', 'Notification', formatter=lambda v, r: 'Notification'),
    Column('message', 'Description', formatter=notif_message),
    Column('engagement', 'Click %', formatter=lambda v, r: "{}%".format(random.randint(2, 99)))
]


class Notifications(Table):
    cls = NotificationSearch
    columns = notification_columns

def segment_count(v, r):
    return r.count


def segment_actions(v, record):
    # FIXME: redefine .btn-danger?
    # TODO: extend use <tr data-object> instead of segment_id?
    return """\
<div class="btn-group btn-group-xs" role=group>
    <a class="btn btn-default" href="#grow-modal" data-toggle=modal data-target="#grow-modal" data-segment="{segment_id}" role="button">Grow</a>
    <a class="btn btn-default" href="#boost-modal" data-toggle=modal data-target="#boost-modal" data-segment="{segment_id}" data-title="Engage a Segment" role="button">Engage</a>
</div>
<div class="btn-group btn-group-xs" role=group>
    <button class=btn type=button data-toggle=modal data-target="#remove-segment-modal" data-icon="&#xe054;" value=Delete></button>
</div>""".format(
        segment_id=record._id,
    )


def date_formatter(v, r):
    return date_format(v)


class Segments(Table):

    cls = SegmentSearch
    columns = [
        Column('name', "Name", sortable=True),
        Column('created', "Created", formatter=date_formatter, sortable=True),
        Column('', 'Members', formatter=segment_count),
        Column('', 'Engagement', formatter=lambda r, v: "...", sortable=True),
        Column('last_notification', "Last Notification", formatter=date_formatter, sortable=True),
        Column('', 'Actions', formatter=segment_actions),
    ]
