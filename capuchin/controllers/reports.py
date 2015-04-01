from flask import Blueprint, render_template, request, g, jsonify, Response, current_app
from flask.views import MethodView
from flask.ext.login import current_user
from capuchin import config
from capuchin import db as dbs
from capuchin.controllers.audience import Create as CreateSegment
from capuchin.models.list import List
from capuchin.models.post import Post
from capuchin.models.segment import Segment
from capuchin.views.tables.dashboard import Posts
from capuchin.views.insights import *
from capuchin.views.insights.charts import \
    FBInsightsPieChart,\
    FBInsightsMultiBarChart,\
    HistogramChart,\
    FreeHistogramChart,\
    SeriesGrowthComparisonChart,\
    WordBubble, \
    HorizontalBarChart

import logging
import json
import time
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
            segments=current_user.client.segments(query={"name":{"$ne":None}}),
        )

class Chart(MethodView):
    charts = {
        "growth_vs_competitors": growth_vs_competitors,
        "total_growth_over_time": growth_over_time,
        "net_growth_per_day": net_growth_per_day,
        "audience_by_source": audience_by_source,
        "post_performance": post_performance,
        "top_cities": top_cities,
        "share_like_ratios": share_like_ratios,
        "audience_location": audience_location,
        "age": age,
        "gender": gender,
        "interests": interests,
        "actions": actions,
        "hours_active": hours_active,
        "city_population": city_population,
    }

    def get(self, chart_id):
        start_ts = request.args.get("start_ts", None)
        end_ts = request.args.get("end_ts", None)
        if not start_ts and not end_ts:
            end_ts = time.time() - 86400
            since = request.args.get("since", None)
            if since:
                if since == 'Last Week':
                    start_ts = time.time() - 86400*7
                elif since == 'All Time':
                    start_ts = 0
                else:
                    start_ts = time.time() - 86400*30
            else:
                start_ts = time.time() - 86400*30

        res = self.charts[chart_id](start=start_ts, end=end_ts, request_args=request.args)
        obj = {'data':res.data}
        try:
            obj['date_format'] = res.date_format
        except:pass
        return jsonify(**obj)

reports.add_url_rule("/", view_func=Index.as_view('index'))
reports.add_url_rule("/chart/<chart_id>", view_func=Chart.as_view('chart'))
reports.add_url_rule("/../audience/segment/create", view_func=CreateSegment.as_view('create_segment'))
