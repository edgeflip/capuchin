from flask import Blueprint, render_template, current_app, redirect, url_for, request, Response, g, jsonify
from flask.views import MethodView
from flask.ext.login import current_user
from capuchin import config
from capuchin import filters
from capuchin.models.post import Post
from capuchin.views.insights.charts import HistogramChart, DualAxisTimeChart, DummyHorizontalBarChart, DummyPieChart, DummyBarChart
from capuchin.views.tables.dashboard import Posts, Notifications
import logging
import slugify
from collections import OrderedDict
import math
import json
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

    def get(self, page=0, template=None):
        q = request.args.get("q", "*")
        q = "*" if not q else q
        posts = Posts(current_user.client)
        tmpl = template if template else "posts/index.html"
        return render_template(
            tmpl,
            posts=posts,
            page=page,
            q=q,
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

def age_graph(post):
    def age_formatter(x, y):
        return "<div class='overhead-popover'>Ages " + str(x) + ": " + str(y) + " engaged users</div>"

    return DummyBarChart(
        'Age',
        [
            ('18-24', 22),
            ('25-34', 34),
            ('35-44', 30),
            ('45-54', 22),
            ('55-64', 30),
            ('65+', 20),
        ],
        tooltip_formatter=age_formatter,
    )


def gender_graph(post):
    return DummyPieChart(
        'Gender',
        {
            'Males': 100,
            'Females': 70,
        }
    )

def interests_graph(post):
    return DummyHorizontalBarChart('Interests', {
        'Environmental Issues': .23,
        'Major League Baseball': .46,
        'Current Events': .35,
    })

def actions_graph(post):
    return DummyHorizontalBarChart('Interests', {
        'Donated to Charity': .42,
        'Attended a Concert': .12,
        'Went on a Vacation': .35,
    })

class Chart(MethodView):
    charts = {
        "engagement":engagement_graph,
        "age":age_graph,
        "gender":gender_graph,
        "interests":interests_graph,
        "actions":actions_graph,
    }

    def get(self, chart_id):
        post_id = request.args.get("post_id")
        post = Post(id=post_id)
        res = self.charts[chart_id](post)
        return jsonify(**dict(data=res.data, date_format=res.date_format))


engagement.add_url_rule("/", view_func=Index.as_view('index'))
engagement.add_url_rule("/<int:page>", view_func=Index.as_view("page"))
engagement.add_url_rule("/view/<id>", view_func=View.as_view("view"))
engagement.add_url_rule("/chart/<chart_id>", view_func=Chart.as_view("chart"))
