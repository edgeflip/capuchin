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

def city_population(start, end):
    return CityPopulation(client=current_user.client, top_n=200)

def top_cities(start, end):
    return TopCities(client=current_user.client, top_n=11)

def audience_location():
    return AudienceLocation(client=current_user.client)

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

def growth_vs_competitors(start, end):
    return DummyHorizontalBarChart('Growth vs Competitors (last week)', {
        'You': 0.03,
        'Greenpeace': 0.01,
        'WWF': 0.07,
        'NRDC': 0.04,
    })
    comparables = \
        [{ 'series': 'insights.{}.page_fans.lifetime', 'display': 'You'}] +\
        [{ 'series': 'insights.{}.competitors.' + competitor.id + '.lifetime', 'display': competitor.name} for competitor in current_user.client.competitors]

    return SeriesGrowthComparisonChart(
        current_user.client,
        comparables,
        buckets='1d',
        start=start,
        end=end,
        date_format = "%m/%d/%y"
    )

def generate_points(daily_values):
    return [
        {
            'ts': int((datetime.date.today() - datetime.timedelta(days_back)).strftime('%s'))*1000,
            'value': v,
        }
        for days_back, v in enumerate(reversed(daily_values))
    ]

def growth_over_time(start, end):

    audience_dataset = generate_points([200, 202, 210, 211, 212, 212, 214, 216, 220, 221, 222, 224, 227, 230, 232, 234, 236, 238, 240, 242, 245, 250, 248, 254, 255, 250])
    pagelike_dataset = generate_points([390, 392, 395, 400, 402, 405, 407, 408, 410, 413, 416, 418, 420, 425, 430, 435, 440, 445, 450, 458, 475, 492, 502, 528, 530, 545])

    comparables = {
        'Audience': {
            'data': audience_dataset,
            'yAxis': 1,
            'type': 'line',
            'color': "#CC3A17",
        },
        'Page Fans': {
            'data': pagelike_dataset,
            'yAxis': 2,
            'type': 'area',
            'color': "#4785AB",
        },
    }

    return DummyDualAxisTimeChart(
        current_user.client,
        comparables,
        date_format = "%m/%d"
    )


def net_growth_per_day(start, end):
    audience_dataset = generate_points([2, 3, 5, -2, 6, 1, -5])
    pagelike_dataset = generate_points([8, 17, 17, 10, 26, 2, 15])

    comparables = {
        'Audience': {
            'data': audience_dataset,
            'yAxis': 1,
            'type': 'line',
            'color': "#CC3A17",
        },
        'Page Fans': {
            'data': pagelike_dataset,
            'yAxis': 1,
            'type': 'line',
            'color': "#4785AB",
        },
    }

    return DummyDualAxisTimeChart(
        current_user.client,
        comparables,
        date_format = "%m/%d"
    )


def audience_by_source(start, end):
    return DummyPieChart('Audience by Source', {
        'Smart Sharing': 25,
        'Email': 87,
        'Facebook': 45,
        'Twitter': 30,
    })


def age_and_gender():
    return [
        {'13-17': 56, '18-24': 22},
        {'13-17': 21, '18-24': 22},
    ]

def gender():
    return AudiencePie(
        current_user.client,
        'gender'
    )


def age():
    def age_formatter(x, y):
        return "<div class='overhead-popover'>Ages " + str(x) + ": " + str(y) + " users</div>"

    def key_formatter(key):
        minimum, maximum = (age.rstrip('.0') for age in key.split('-'))
        if maximum == "*":
            return "{}+".format(minimum)
        elif minimum == "*":
            return "{}-".format(maximum)
        else:
            return "-".join((minimum, maximum))

    ranges = [
          {
            "from": 13,
            "to": 17
          },
          {
            "from": 18,
            "to": 24
          },
          {
            "from": 25,
            "to": 34
          },
          {
            "from": 35,
            "to": 44
          },
          {
            "from": 45,
            "to": 54
          },
          {
            "from": 55,
            "to": 64
          },
          {
            "from": 65
          }
    ]
    return AudienceRangeBar(
        current_user.client,
        field="age",
        ranges=ranges,
        tooltip_formatter=age_formatter,
        key_formatter=key_formatter,
    )


def interests():
    return DummyHorizontalBarChart('Interests', {
        'Education': .09,
        'Gender and sexuality': .09,
        'Charitable donations': .12,
        'Food and drink': .18,
        'Volunteering': .24,
        'Travel': .30,
        'Politics (all)': .75,
        'Politics (left-leaning)': .72,
        'Nonprofits and advocacy': .85,
        'Environmental issues': .97,
    })

def actions():
    return DummyHorizontalBarChart('Interests', {
        'Donated to Charity': .42,
        'Attended a Concert': .12,
        'Went on a Vacation': .35,
    })


def hours_active():
    def hour_tooltip_formatter(x, y):
        hour = int(x)
        if hour == 0:
            pretty_hour = 'midnight'
        elif hour < 12:
            pretty_hour = '{} AM'.format(hour)
        elif hour == 12:
            pretty_hour = 'noon'
        else:
            pretty_hour = '{} PM'.format(hour-12)
        return "<div class='overhead-popover'>" + pretty_hour + ": " + "{0:.1f}".format(y) + " average users active</div>"

    return FBInsightsDiscreteBarChart(
        current_user.client,
        typ="page_fans_online.day",
        tooltip_formatter=hour_tooltip_formatter,
    )


def post_performance(start, end):
    #posts = Post.records(current_user.client, "*", 0, 10, None)
    #for post in posts.hits:
        #s = ",".join([post.id, str(len(post.comments)), str(len(post.likes)), post.created_time, post.message])
        #logging.info(s)
    views_dataset = [
        {
            'post_id': '123658315_2346352357',
            'ts': 1425069150000,
            'value': 145,
            'views': 145,
            'engagement': 32,
            'message': "What we're up to at Edgeflip",
        },
        {
            'post_id': '123658315_2346352359',
            'ts': 1425241957000,
            'value': 42,
            'views': 42,
            'engagement': 40,
            'message': 'Edgeflip is proud to support HeForShe',
        },
        {
            'post_id': '123658315_2346352358',
            'ts': 1425501161000,
            'value': 360,
            'views': 360,
            'engagement': 28,
            'message': 'Redeeming the Humble Thank You Page',
        },
        {
            'post_id': '123658315_2346352358',
            'ts': 1425588670000,
            'value': 98,
            'views': 98,
            'engagement': 26,
            'message': "We're doing a webinar",
        },
    ]
    engagement_dataset = [
        {
            'post_id': '123658315_2346352357',
            'ts': 1425069150000,
            'value': 32,
            'views': 145,
            'engagement': 32,
            'message': "What we're up to at Edgeflip",
        },
        {
            'post_id': '123658315_2346352359',
            'ts': 1425241957000,
            'value': 40,
            'views': 42,
            'engagement': 40,
            'message': 'Edgeflip is proud to support HeForShe',
        },
        {
            'post_id': '123658315_2346352358',
            'ts': 1425501161000,
            'value': 28,
            'views': 360,
            'engagement': 28,
            'message': 'Redeeming the Humble Thank You Page',
        },
        {
            'post_id': '123658315_2346352358',
            'ts': 1425588670000,
            'value': 26,
            'views': 98,
            'engagement': 26,
            'message': "We're doing a webinar",
        },
    ]
    benchmark_dataset = [
        {
            'ts': 1425069150000,
            'value': 32,
            'engagement': 32,
        },
        {
            'ts': 1425588670000,
            'value': 32,
            'engagement': 32,
        },
    ]

    comparables = {
        'Views': {
            'data': views_dataset,
            'yAxis': 1,
            'type': 'line',
            'color': "#4785AB",
        },
        'Engagement %': {
            'data': engagement_dataset,
            'yAxis': 2,
            'type': 'line',
            'color': "#CC3A17",
        },
        'Benchmark %': {
            'data': benchmark_dataset,
            'yAxis': 2,
            'type': 'line',
            'color': "#363738",
        },
    }

    return DummyDualAxisTimeChart(
        current_user.client,
        comparables,
    )



def share_like_ratios():
    return DummyHorizontalBarChart('Share-Like Ratios (last five posts)', {
        'You': 0.06,
        'Greenpeace': 0.04,
        'WWF': 0.07,
        'NRDC': 0.04,
    })


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
