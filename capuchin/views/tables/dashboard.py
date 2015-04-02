from flask import current_app, url_for
from capuchin.models.post import Post
from capuchin.models.notification import Notification
from capuchin.util import date_format
from capuchin.views.tables import Column, Table, MongoTable
import random
import logging

# TODO move all the html into templates and/or macros


def post_type(val, record):
    try:
        return "<img src=\"{}\" />".format(record.icon)
    except:
        return ""


def post_targeting(val, record):
    return """<span class="icon-globe"></span>"""


def pluralize(number, singular='', plural='s'):
    return singular if number == 1 else plural


def post_engagement(val, record):
    num_comments = len(record.comments)
    num_likes = len(record.likes)
    return (
        "<p>{} like{}</p>"
        "<p>{} comment{}</p>"
        .format(
            num_likes,
            pluralize(num_likes),
            num_comments,
            pluralize(num_comments),
        )
    )


def post_actions(val, record):
    return """\
<div class="btn-group btn-group-xs" role="group" aria-label="...">
    <a class="btn btn-default" href="{view_href}">View</a>
    <a class="btn btn-default" href="#boost-modal" data-toggle="modal" data-target="#boost-modal" data-post="{post_id}">Boost</a>
</div>""".format(
        post_id=record.id,
        view_href=url_for('engagement.view', id=record.id),
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
    Column('', 'Notification', formatter=lambda v, r: 'Notification'),
    Column('', 'Segment', formatter=lambda v, r: r.segment.name),
    Column('message', 'Description', formatter=notif_message),
    Column('engagement', 'Click %', formatter=lambda v, r: "{}%".format(random.randint(2, 99)))
]


class Notifications(MongoTable):
    cls = Notification
    columns = notification_columns

    def build_rows(self, records):
        real_rows = super(Notifications, self).build_rows(records)

        data = (
            ('3/19/2015', 'Notification', 'Urban 18-35', '{Name}, take five minutes to watch this video.', '54%'),
            ('3/18/2015', 'Notification', 'Politically Active', '{Name}, help us move the political needle on this important issue!', '63%'),
            ('3/17/2015', 'Notification', 'All Supporters', '{Name}, you need to see this...', '41%'),
        )
        for row in data:
            td = [u"<tr data-url=\"None\">"]
            for field in row:
                td.append(u"<td>{}</td>".format(field))
            td.append(u"</tr>")
            real_rows.append(u"".join(td))
        return real_rows


    def get_records(self, q, from_, size, sort):
        records, total = super(Notifications, self).get_records(q, from_, size, sort)
        return records, total+3
