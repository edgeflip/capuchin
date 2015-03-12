from flask import Blueprint, render_template, current_app, redirect, url_for, request, Response, g, jsonify
from flask.views import MethodView
from flask.ext.login import current_user
from capuchin import config
from capuchin import filters
from capuchin.models.post import Post
from capuchin.views.insights.charts import HistogramChart
from capuchin.views.tables.dashboard import Posts, Notifications
import logging
import slugify
import math
import json
import time

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

def engagement_graph(post):
    date_format = "%Y-%m-%dT%H:%M:%S+0000"
    tm = time.mktime(
        time.strptime(
            post.created_time,
            date_format
        )
    )
    return HistogramChart(
        current_user.client,
        [
            {"type":"post.{}.likes".format(post.id), "display":"Likes"},
            {"type":"post.{}.comments".format(post.id), "display":"Comments"},
            {"type":"post.{}.shares".format(post.id), "display":"Shares"},
        ],
        prefix="insights",
        where="WHERE time > {}s".format(tm),
        buckets="1d",
        date_format="%m/%d"
    )


class Chart(MethodView):
    charts = {
        "engagement":engagement_graph
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
