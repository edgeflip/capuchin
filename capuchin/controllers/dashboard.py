from flask import Blueprint, render_template, request, g
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
    FreeHistogramChart
import logging
import json

db = Blueprint(
    'dashboard',
    __name__,
    template_folder=config.TEMPLATES,
)

class DashboardDefault(MethodView):

    def get(self):

        city_population = CityPopulation(client=current_user.client)

        like_gains = FreeHistogramChart(
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

        likes = FreeHistogramChart(
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

        page_by_type = FBInsightsPieChart(
            current_user.client,
            typ="page_stories_by_story_type.day",
        )

        engaged_users = FBInsightsMultiBarChart(
            current_user.client,
            [
                {"type":"page_engaged_users.day", "display":"Engaged Users"},
                {"type":"page_consumptions.day", "display":"Page Consumptions"},
            ],
            date_format = "%m/%d/%y"
        )

        notifications = HistogramChart(
            current_user.client,
            [
                {"type":"notification_sent", "display":"Sent"},
                {"type":"notification_failure", "display":"Failures"},
            ],
            prefix="events",
            where="",
            date_format = "%H:%M:00",

        )

        online = FBInsightsPieChart(
            current_user.client,
            "page_fans_online.day",
        )

        country = FBInsightsPieChart(
            current_user.client,
            typ="page_impressions_by_country_unique.day",
        )


        first = request.args.get("first")
        lists = current_user.client.lists()
        segments = current_user.client.segments(query={"name":{"$ne":None}})
        return render_template(
            "dashboard/index.html",
            lists=lists,
            segments=segments,
            first=first,
            page_by_type=page_by_type,
            engaged_users=engaged_users,
            country=country,
            online=online,
            notifications=notifications,
            likes=likes,
            like_gains = like_gains,
            city_population = city_population,
        )

db.add_url_rule("/", view_func=DashboardDefault.as_view('index'))
