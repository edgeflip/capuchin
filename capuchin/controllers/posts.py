from flask import Blueprint, render_template, current_app, redirect, url_for, request, Response, g
from flask.views import MethodView
from flask.ext.login import current_user
from capuchin import config
from capuchin import filters
from capuchin.models.post import Post
from capuchin.insights.charts import HistogramChart
import logging
import slugify
import math
import json
import time

posts = Blueprint(
    'posts',
    __name__,
    template_folder=config.TEMPLATES,
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

class PostsIndex(MethodView):

    def get(self, page=0, template=None):
        q = request.args.get("q", "*")
        q = "*" if not q else q
        records = Post.records(client=current_user.client, q=q, from_=page*config.RECORDS_PER_PAGE)
        logging.info(records)
        tmpl = template if template else "posts/index.html"
        return render_template(
            tmpl,
            records=records['hits'],
            total=records['total'],
            pagination=create_pagination(records['total'], page),
            page=page,
            q = q if q != "*" else ""
        )

    def post(self, page=0):
        return self.get(page=page, template="posts/records.html")

class PostsView(MethodView):

    def get(self, id):
        date_format = "%Y-%m-%dT%H:%M:%S+0000"
        post = g.ES.get(
            config.ES_INDEX,
            id,
            config.POST_RECORD_TYPE,
            fields=['message', 'created_time'],
            _source=False,
        )
        tm = time.mktime(
            time.strptime(
                post['fields']["created_time"][0],
                date_format
            )
        )
        engagement = HistogramChart(
            current_user.client,
            [
                {"type":"post.{}.likes".format(post.get("_id")), "display":"Likes"},
                {"type":"post.{}.comments".format(post.get("_id")), "display":"Comments"},
                {"type":"post.{}.shares".format(post.get("_id")), "display":"Shares"},
            ],
            prefix="insights",
            where="WHERE time > {}s".format(tm),
            buckets="1d",
            date_format="%m/%d"
        )
        return render_template(
            "posts/view.html",
            post=post,
            engagement=engagement,
        )

posts.add_url_rule("/posts", view_func=PostsIndex.as_view('index'))
posts.add_url_rule("/posts/<int:page>", view_func=PostsIndex.as_view("page"))
posts.add_url_rule("/posts/view/<id>", view_func=PostsView.as_view("view"))