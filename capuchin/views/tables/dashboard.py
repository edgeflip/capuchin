from flask import current_app
from flask_login import current_user
from capuchin.models.post import Post
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

post_columns = [
    Column('created_time', "Published", sortable=True),
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
