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
    SeriesGrowthComparisonChart,\
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
    time_based_charts = {
        "growth_vs_competitors": growth_vs_competitors,
        "total_growth_over_time": growth_over_time,
        "audience_by_source": audience_by_source,
    }
    regular_charts = {
        "city_population": city_population,
        "interests": interests,
        "actions": actions,
        "hours_active": hours_active,
    }


    def get(self, chart_id):
        start_ts = request.args.get("start_ts", None)
        end_ts = request.args.get("end_ts", None)
        if chart_id in self.time_based_charts:
            res = self.time_based_charts[chart_id](start=start_ts, end=end_ts)
        else:
            res = self.regular_charts[chart_id]()
        obj = {'data':res.data}
        try:
            obj['date_format'] = res.date_format
        except:pass
        return jsonify(**obj)

reports.add_url_rule("/", view_func=Index.as_view('index'))
reports.add_url_rule("/chart/<chart_id>", view_func=Chart.as_view('chart'))
