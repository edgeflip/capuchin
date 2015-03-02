POST_INSIGHTS = [
    "likes",
    "comments",
    "attachments",
]

from capuchin.views.insights.charts import *
from capuchin.views.insights.geo import *

from flask_login import current_user

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
    if lw:
        diff = ((tw-lw)/lw)*100
    else:
        diff = 100
    return {'change':diff, 'total':tw}
