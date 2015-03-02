from flask import Blueprint, render_template, request, g, jsonify, Response, current_app
from flask.views import MethodView
from flask.ext.login import current_user
from capuchin import config
from capuchin import db as dbs
from capuchin.models.list import List
from capuchin.models.post import Post
from capuchin.models.segment import Segment
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

from capuchin.views.insights.geo import CityPopulation

import logging
import json
from bunch import Bunch

reports = Blueprint(
    'reports',
    __name__,
    template_folder=config.TEMPLATES,
    url_prefix="/reports",
)


class Index(MethodView):

    def get(self):
        return render_template(
            "reports/index.html",
        )

class Chart(MethodView):
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
    }


    def get(self, chart_id):
        res = self.charts[chart_id]()
        obj = {'data':res.data}
        try:
            obj['date_format'] = res.date_format
        except:pass
        return jsonify(**obj)

reports.add_url_rule("/", view_func=Index.as_view('index'))
reports.add_url_rule("/chart/<chart_id>", view_func=Chart.as_view('chart'))
