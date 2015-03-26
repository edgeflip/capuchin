from flask import Blueprint, render_template, request, g, jsonify, Response, current_app
from flask.views import MethodView
from flask.ext.login import current_user
from capuchin import config
from capuchin import db as dbs
from capuchin.models.list import List
from capuchin.models.post import Post
from capuchin.models.segment import Segment
from capuchin.controllers.tables import render_table
from capuchin.views.tables.dashboard import Posts
from capuchin.views.insights.geo import CityPopulation
from capuchin.views.insights import *
from capuchin.views.insights.charts import \
    FBInsightsPieChart,\
    FBInsightsMultiBarChart,\
    HistogramChart,\
    FreeHistogramChart,\
    WordBubble, \
    HorizontalBarChart

import logging
import json
from bunch import Bunch

db = Blueprint(
    'dashboard',
    __name__,
    template_folder=config.TEMPLATES,
)

@db.context_processor
def notification_creation():
    return {'notification':{
        'posts':Post.records(client=current_user.client),
        'messages':config.MESSAGES
    }
}

class DashboardDefault(MethodView):

    def get(self):
        first = request.args.get("first")
        lists = current_user.client.lists()
        segments = current_user.client.segments(query={"name":{"$ne":None}})
        posts = render_table(Posts)
        if not posts: posts = Posts(current_user.client).render(size=5, pagination=False)
        try:
            like_change = like_weekly_change()
            engagement_change = engagement_weekly_change()
        except:
            like_change = {'change':0, 'total':0}
            engagement_change = {'change':0, 'total':0}

        return render_template(
            "dashboard/index.html",
            posts=posts,
            like_change=like_change,
            engagement_change=engagement_change,
            lists=lists,
            segments=segments,
            first=first,
        )

class DashboardChart(MethodView):
    charts = {
        "page_by_type":page_by_type,
        "engaged_users":engaged_users,
        "country":country,
        "online":online,
        "notifications":notifications,
        "likes":likes,
        "like_gains":like_gains,
        "city_population": city_population,
        "referrers":referrers,
        "top_words":top_words,
        "top_likes":top_likes,
        "total_growth_over_time": growth_over_time,
    }


    def get(self, chart_id):
        start_ts = request.args.get("start_ts", None)
        end_ts = request.args.get("end_ts", None)
        res = self.charts[chart_id](start=start_ts, end=end_ts)
        obj = {'data':res.data}
        try:
            obj['date_format'] = res.date_format
        except:pass
        return jsonify(**obj)

db.add_url_rule("/", view_func=DashboardDefault.as_view('index'))
db.add_url_rule("/chart/<chart_id>", view_func=DashboardChart.as_view('chart'))
