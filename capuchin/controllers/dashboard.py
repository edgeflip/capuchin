from flask import Blueprint, render_template, request, g, jsonify
from flask.views import MethodView
from flask.ext.login import current_user
from capuchin import config
from capuchin.models.list import List
from capuchin.models.segment import Segment
from capuchin.insights.geo import CityPopulation
from capuchin.insights.charts import \
    FBInsightsPieChart,\
    FBInsightsMultiBarChart,\
    HistogramChart,\
    FreeHistogramChart,\
    WordBubble
import logging
import json

db = Blueprint(
    'dashboard',
    __name__,
    template_folder=config.TEMPLATES,
)

def city_population():
    return CityPopulation(client=current_user.client)

def top_words():
    return WordBubble(client=current_user.client)

def referrers():
    referrers = FreeHistogramChart(
        current_user.client,
        [
            {
                "display":"Referrers",
                "q":"SELECT SUM(value), type FROM insights.{}.page_views_external_referrals.day GROUP BY time(32d), type fill(0)",
            }

        ],
        date_format = "%m/%y",
        massage=False
    )

    objs = {}
    for i in referrers.data['Referrers']['values'][0]['points']:
        objs.setdefault(i[2], {
            "total":0,
            "articles":[]
        })
        objs[i[2]]['total']+=i[1]
        objs[i[2]]['articles'].append([i[0], i[1]])

    referrers.data = []
    for k,v in objs.iteritems():
        v['name'] = k
        referrers.data.append(v)

    return referrers


def like_gains():
    return FreeHistogramChart(
        current_user.client,
        [
            {
                "display":"Net Likes",
                "q":"SELECT MEDIAN(value) FROM insights.{}.page_fans.lifetime GROUP BY time(2d)",

            },
            {
                "display":"Like Change",
                "q":"SELECT DIFFERENCE(value) FROM insights.{}.page_fans.lifetime GROUP BY time(2d)",
                "kwargs":{"bar":True}
            }
        ],
        date_format = "%m/%d/%y"
    )

def likes():
    return FreeHistogramChart(
        current_user.client,
        [
            {
                "display":"Likes",
                "q": "SELECT value FROM insights.{}.page_fan_adds.day",
            },
            {
                "display":"Unlikes",
                "q": "SELECT value*-1 FROM insights.{}.page_fan_removes.day",
            },
            {
                "display":"Paid Likes",
                "q":"SELECT value FROM insights.{}.page_fan_adds_by_paid_non_paid_unique.day WHERE type='paid'",
            }
        ],
        date_format = "%m/%d/%y"
    )

def page_by_type():
    return FBInsightsPieChart(
        current_user.client,
        typ="page_stories_by_story_type.day",
    )

def engaged_users():
    return FBInsightsMultiBarChart(
        current_user.client,
        [
            {"type":"page_engaged_users.day", "display":"Engaged Users"},
            {"type":"page_consumptions.day", "display":"Page Consumptions"},
        ],
        date_format = "%m/%d/%y"
    )

def notifications():
    return HistogramChart(
        current_user.client,
        [
            {"type":"notification_sent", "display":"Sent"},
            {"type":"notification_failure", "display":"Failures"},
        ],
        prefix="events",
        where="",
        date_format = "%H:%M:00",
    )

def online():
    return FBInsightsPieChart(
        current_user.client,
        "page_fans_online.day",
    )

def country():
    return FBInsightsPieChart(
        current_user.client,
        typ="page_impressions_by_country_unique.day",
    )

class DashboardDefault(MethodView):

    def get(self):
        first = request.args.get("first")
        lists = current_user.client.lists()
        segments = current_user.client.segments(query={"name":{"$ne":None}})
        return render_template(
            "dashboard/index.html",
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
    }


    def get(self, chart_id):
        res = self.charts[chart_id]()
        obj = {'data':res.data}
        try:
            obj['date_format'] = res.date_format
        except:pass
        return jsonify(**obj)

db.add_url_rule("/", view_func=DashboardDefault.as_view('index'))
db.add_url_rule("/chart/<chart_id>", view_func=DashboardChart.as_view('chart'))
