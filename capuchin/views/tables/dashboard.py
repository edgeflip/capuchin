import logging
import random

from flask import current_app, url_for

from capuchin.models.notification import Notification
from capuchin.models.post import Post
from capuchin.util import date_format
from capuchin.views.tables import Column, Table, MongoTable

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
    # TODO: use <tr data-object> instead of post_id?
    return """\
<div class="btn-group btn-group-xs" role="group" aria-label="...">
    <a class="btn btn-default" href="{view_href}">View</a>
    <a class="btn btn-default" href="#boost-modal" data-toggle="modal" data-target="#boost-modal" data-post="{post_id}" data-title="Boost a Post">Boost</a>
</div>""".format(
        post_id=record.id,
        view_href=url_for('engagement.view', id=record.id),
    )


def post_message(val, record):
    logging.debug(val)

    try:
        img = u'<img class="table-image pull-left" src="{}">'.format(record.picture)
    except AttributeError:
        img = u''

    truncated_val = current_app.jinja_env.filters['truncate'](val, 120)
    logging.debug(truncated_val)
    message = u'<p class=post-detail>{}</p>'.format(truncated_val)

    return img + message


def post_reach(value, record):
    return u'<p data-post="{post_id}" class=post-reach-chart>&hellip;</p>'.format(post_id=record.id)


def date_formatter(v, r):
    return date_format(r.created_time)


def truncate(v, chars):
    return current_app.jinja_env.filters['truncate'](v, chars)

class Posts(Table):

    cls = Post
    columns = [
        Column('created_time', "Published", formatter=date_formatter, sortable=True),
        Column('message', "Post", formatter=post_message, sortable=True),
        Column('', "Type", formatter=post_type),
        # Column('', "Targeting", formatter=post_targeting), # FIXME: do we need this?
        Column('', "Reach", formatter=post_reach),
        Column('', "Engagment", formatter=post_engagement),
        Column('', '', formatter=post_actions, cls="actions"),
    ]


class Notifications(MongoTable):
    cls = Notification
    columns = [
        Column('created', 'Date', formatter=lambda v, r: date_format(v), sortable=True),
        Column('message', 'Description', formatter=lambda v, r: truncate(v, 25), sortable=True),
        Column('segment', 'Segment', formatter=lambda v, r: r.segment.name, sortable=True),
        Column('post', 'Content', formatter=lambda v, r: truncate(r.get_content(), 25), sortable=True),
        Column('engagement', 'Click %', formatter=lambda v, r: "{}%".format(random.randint(2, 99)))
    ]

    fake_data = (
            ['03/19/2015', '{Name}, take five minutes to watch this video.', 'Urban 18-35', '54%'],
            ['03/18/2015', '{Name}, help us move the political needle on this important issue!', 'Politically Active', '63%'],
            ['03/17/2015', '{Name}, you need to see this...', 'All Supporters', '41%'],
    )

    def get_records(self, q, from_, size, sort):
        records, total = super(Notifications, self).get_records(q, from_, size, sort)
        return records, total+3


class ClientNotifications(Notifications):
    def build_rows(self, records):
        real_rows = super(ClientNotifications, self).build_rows(records)

        for row in self.fake_data:
            td = [u"<tr>"]
            td.append(u"<td>{}</td>".format(row[0]))
            td.append(u"<td>{}</td>".format(row[1]))
            td.append(u"<td>{}</td>".format(row[2]))
            td.append(u"<td>{}</td>".format("Merchants of Doubt, a new documentary..."))
            td.append(u"<td>{}</td>".format(row[3]))
            td.append(u"</tr>")
            real_rows.append(u"".join(td))
        return real_rows


class PostNotifications(Notifications):
    columns = [
        Column('created', 'Date', formatter=lambda v, r: date_format(v), sortable=True),
        Column('message', 'Description', formatter=lambda v, r: truncate(v, 25), sortable=True),
        Column('segment', 'Segment', formatter=lambda v, r: r.segment.name, sortable=True),
        Column('engagement', 'Click %', formatter=lambda v, r: "{}%".format(random.randint(2, 99)))
    ]

    def build_rows(self, records):
        real_rows = super(PostNotifications, self).build_rows(records)

        for row in self.fake_data:
            td = [u"<tr>"]
            for field in row:
                td.append(u"<td>{}</td>".format(field))
            td.append(u"</tr>")
            real_rows.append(u"".join(td))
        return real_rows
