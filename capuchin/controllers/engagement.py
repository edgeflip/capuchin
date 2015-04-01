from flask import Blueprint, render_template, request, jsonify
from flask.views import MethodView
from flask.ext.login import current_user
from capuchin import config
from capuchin.models.post import Post
from capuchin.views.insights.charts import DualAxisTimeChart
from capuchin.views.insights import age, gender, interests
from capuchin.views.tables.dashboard import Posts, Notifications
from capuchin.controllers.tables import render_table
import logging
from collections import OrderedDict
import math
import time
import datetime

engagement = Blueprint(
    'engagement',
    __name__,
    template_folder=config.TEMPLATES,
    url_prefix="/engagement",
)

def create_pagination(total_records, current_page=0):
    tp = math.ceil(total_records/config.RECORDS_PER_PAGE)
    total_pages = tp if tp <= 20 else 20
    page = {
        "previous": current_page-1 if current_page > 0 else 0,
        "next": current_page+1 if current_page < total_pages else total_pages,
        "total_pages": int(total_pages)
    }
    return page

class Index(MethodView):

    def get(self, page=0, template='posts/index.html'):
        query = request.args.get('q') or '*'

        posts = render_table(Posts)
        if not posts:
            posts = Posts(current_user.client).render(
                q=query,
                sort=('created_time', 'desc'),
            )

        return render_template(
            template,
            posts=posts,
            page=page,
            q=query,
        )

    def post(self, page=0):
        return self.get(page=page, template="posts/records.html")

class View(MethodView):

    def get(self, id):
        post = Post(id=id)
        notifications = Notifications(current_user.client)
        logging.info(post)
        return render_template(
            "posts/view.html",
            post=post,
            notifications=notifications,
        )


def post_url_prefix(post):
    return "insights.{}.post." + post.id + "."

def engagement_graph(post):
    date_format = "%Y-%m-%dT%H:%M:%S+0000"
    post_time = datetime.datetime.strptime(
        post.created_time,
        date_format
    )
    start = time.mktime(post_time.timetuple())
    end = time.mktime((post_time + datetime.timedelta(days=3)).timetuple())
    comparables = OrderedDict()
    comparables['Post Likes'] = {
        'series': post_url_prefix(post) + "likes",
        'yAxis': 1,
        'type': 'line',
        'fill_color': "#CC3A17",
    }
    comparables['Post Shares'] = {
        'series': post_url_prefix(post) + "shares",
        'yAxis': 1,
        'type': 'line',
        'fill_color': "#8561A9",
    }
    comparables['Post Comments'] = {
        'series': post_url_prefix(post) + "comments",
        'yAxis': 1,
        'type': 'line',
        'fill_color': "#4785AB",
    }
    return DualAxisTimeChart(
        current_user.client,
        comparables,
        prefix="insights",
        start=start,
        end=end,
        buckets='1h',
        date_format="%-m-%d %-I %p",
    )

class Chart(MethodView):
    post_charts = {
        "engagement":engagement_graph,
    }
    fake_charts = {
        "age":age,
        "gender":gender,
        "interests":interests,
    }

    def get(self, chart_id):
        if chart_id in self.post_charts:
            post_id = request.args.get("post_id")
            post = Post(id=post_id)
            res = self.post_charts[chart_id](post)
            return jsonify(**dict(data=res.data, date_format=res.date_format))
        else:
            res = self.fake_charts[chart_id](None, None, {})
            return jsonify(**dict(data=res.data))


engagement.add_url_rule("/", view_func=Index.as_view('index'))
engagement.add_url_rule("/<int:page>", view_func=Index.as_view("page"))
engagement.add_url_rule("/view/<id>", view_func=View.as_view("view"))
engagement.add_url_rule("/chart/<chart_id>", view_func=Chart.as_view("chart"))
