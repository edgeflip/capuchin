from flask import Blueprint, render_template, request, g, jsonify, Response
from flask.views import MethodView
from flask.ext.login import current_user
from capuchin import config
from capuchin import db as dbs
from capuchin.models.list import List
from capuchin.models.post import Post
from capuchin.models.segment import Segment
from capuchin.insights.geo import CityPopulation
from capuchin.insights.charts import \
    FBInsightsPieChart,\
    FBInsightsMultiBarChart,\
    HistogramChart,\
    FreeHistogramChart,\
    WordBubble, \
    HorizontalBarChart
import logging
import json

db = Blueprint(
    'dashboard',
    __name__,
    template_folder=config.TEMPLATES,
)

def top_likes():
    return HorizontalBarChart(
        client=current_user.client,
        facet="likes.name"
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

def like_weekly_change():
    INFLUX = dbs.init_influxdb()
    res = INFLUX.query(
        "SELECT DIFFERENCE(value) FROM insights.{}.page_fans.lifetime WHERE time>now()-1w".format(current_user.client._id)
    )
    res2 = INFLUX.query(
        "SELECT value FROM insights.{}.page_fans.lifetime LIMIT 1".format(current_user.client._id)
    )
    change = res[0]['points'][0][1]*-1
    total = res2[0]['points'][0][2]
    perc = (float(change)/float(total))*100
    return {'change':perc, 'total':total}

def engagement_weekly_change():
    INFLUX = dbs.init_influxdb()
    last_week = INFLUX.query(
        "SELECT SUM(value) FROM insights.{}.page_engaged_users.day WHERE time<now()-1w AND time > now()-2w".format(current_user.client._id)
    )
    this_week = INFLUX.query(
        "SELECT SUM(value) FROM insights.{}.page_engaged_users.day WHERE time>now()-1w".format(current_user.client._id)
    )
    logging.info(last_week)
    logging.info(this_week)
    lw = float(last_week[0]['points'][0][1])
    tw = float(this_week[0]['points'][0][1])
    diff = ((tw-lw)/lw)*100
    return {'change':diff, 'total':tw}


class RecentActivity(MethodView):

    def get(self):
        posts = Post.records(current_user.client, size=5, ret_obj=True)
        return Response(json.dumps([p.json() for p in posts]))

class DashboardDefault(MethodView):

    def get(self):
        first = request.args.get("first")
        lists = current_user.client.lists()
        segments = current_user.client.segments(query={"name":{"$ne":None}})
        like_change = like_weekly_change()
        engagement_change = engagement_weekly_change()
        return render_template(
            "dashboard/index.html",
            #posts=posts,
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
db.add_url_rule("/recent_activity", view_func=RecentActivity.as_view('recent_activity'))
