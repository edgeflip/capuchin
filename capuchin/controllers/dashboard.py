from flask import Blueprint, render_template, request
from flask.views import MethodView
from flask.ext.login import current_user
from capuchin import INFLUX
from capuchin import config
from capuchin.models.list import List
from capuchin.models.segment import Segment
import logging
import json

db = Blueprint(
    'dashboard',
    __name__,
    template_folder=config.TEMPLATES,
)

class DashboardDefault(MethodView):

    def get(self):
        page_adds = INFLUX.query(
            "SELECT value FROM insights.{}.page_consumptions;".format(
                current_user.client._id
            )
        )
        page_adds = [{"x":a[0], "y":a[2]} for a in page_adds[0]['points']]
        page_adds.reverse()
        q = "SELECT sum(value), typ FROM /^insights.{}.page_stories_by_story_type.*/ WHERE time < now() GROUP BY typ;".format(
            current_user.client._id
        )
        page_stories = INFLUX.query(q)
        page_stories = [{
            "label":a['points'][0][2],
            "value":a['points'][0][1]
        } for a in page_stories]

        page_posts = INFLUX.query(
            "SELECT value FROM insights.{}.page_engaged_users;".format(
                current_user.client._id
            )
        )
        page_posts = [{"x":a[0], "y":a[2]} for a in page_posts[0]['points']]
        page_posts.reverse()

        first = request.args.get("first")
        lists = current_user.client.lists()
        segments = current_user.client.segments(query={"name":{"$ne":None}})
        return render_template(
            "dashboard/index.html",
            lists=lists,
            segments=segments,
            first=first,
            page_adds=json.dumps(page_adds),
            page_stories=json.dumps(page_stories),
            page_posts=json.dumps(page_posts),
        )

db.add_url_rule("/", view_func=DashboardDefault.as_view('index'))
