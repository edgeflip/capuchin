from flask import current_app
from flask_login import current_user
from capuchin.models.post import Post
from capuchin.models.notification import Notification
from capuchin.util import date_format
from capuchin.views.tables import Column, Table

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
            <button type="button" class="btn btn-default">Respond</button>
            <button type="button" class="btn btn-default">Dismiss</button>
        </div>"""

def post_message(val, record):
    try:
        img = "<div class=\"col-md-6\"><img class=\"table-image\" src=\"{}\" /></div>".format(record.picture)
    except:
        img = ""
    mes = "<div class=\"col-md-6\">{}</div>".format(current_app.jinja_env.filters['truncate'](val, 30))
    return "{}{}".format(img, mes)

def date_formatter(v, r):
    return date_format(r.created_time)

def post_alerts(v, r):
    notes = Notification.find({"post_id":r.id})
    n_table = ["<table class='table'>"]
    n_table.append("<thead><tr><th>Sent</th><th>Preview</th><th>Targeting</th><th>Reach</th><th>Engagement</th></tr></thead><tbody>")
    for n in notes:
        n_table.append("<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            date_format(n.created),
            current_app.jinja_env.filters['truncate'](n.message, 25),
            n.segment.name,
            "1,100",
            "1,090",
        ))
    n_table.append("</tbody></table>")
    #return '<a tabindex="0" class="btn btn-lg btn-danger" role="button" data-toggle="popover" data-trigger="focus" title="Dismissible popover" data-content="And heres some amazing content. Its very engaging. Right?">Dismissible popover</a>'
    return "<a \
        tabbindex=\"0\" \
        role=\"button\" \
        data-trigger=\"focus\" \
        data-html=\"true\" \
        class=\"btn btn-primary\" \
        data-toggle=\"popover\" \
        data-placement=\"bottom\" \
        title=\"Notifications\" \
        data-content=\"{}\"> \
        Alerts \
        </a>".format("".join(n_table))

post_columns = [
    Column('created_time', "Published", formatter=date_formatter, sortable=True),
    Column('message', "Post", formatter=post_message, sortable=True),
    Column('', "Type", formatter=post_type),
    Column('', "Targeting", formatter=post_targeting),
    Column('', "Reach", formatter=lambda v, r: "1,090"),
    Column('', "Engagment", formatter=post_engagement),
    Column('', 'Alerts', formatter=post_alerts),
    Column('', '', formatter=post_actions, cls="actions"),
]

class Posts(Table):
    cls = Post
    columns = post_columns
