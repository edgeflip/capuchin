POST_INSIGHTS = [
    "likes",
    "comments",
    "attachments",
]

from capuchin.views.insights.charts import *
from capuchin.views.insights.geo import *
from capuchin.models.post import Post
from capuchin.db import init_influxdb

from flask_login import current_user
from flask import current_app

import random

date_format = "%Y-%m-%dT%H:%M:%S+0000"

def top_likes():
    return HorizontalBarChart(
        client=current_user.client,
        facet="likes.name"
    )

def city_population(start, end, request_args):
    return CityPopulation(client=current_user.client, top_n=200)

def top_cities(start, end, request_args):
    return TopCities(client=current_user.client, top_n=11, cities_override=request_args.get('value', None))

def audience_location(start, end, request_args):
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

def growth_vs_competitors(start, end, request_args):
    return DummyHorizontalBarChart('Growth vs Competitors (last week)', {
        'You': random.random()/10,
        'Greenpeace': random.random()/10,
        'WWF': random.random()/10,
        'NRDC': random.random()/10,
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

def growth_over_time(start, end, request_args):

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


def net_growth_per_day(start, end, request_args):
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


def audience_by_source(start, end, request_args):
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

def gender(start, end, request_args):
    if 'chart' in request_args:
        if request_args['chart'] == 'gender':
            gender = request_args['label']
            if gender == 'male':
                args = { 'male': 100, 'female': 0, }
            else:
                args = { 'female': 100, 'male': 0, }
        else:
            dice_roll = random.randint(30, 70)
            args = { 'male': dice_roll, 'female': 100-dice_roll }

        return DummyPieChart(
            'Gender',
            args
        )

    else:
        return AudiencePie(
            current_user.client,
            'gender'
        )


def age(start, end, request_args):
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
    randomize = False
    solo = None
    if 'chart' in request_args:
        if request_args['chart'] == 'age':
            solo = request_args['label']
        else:
            randomize = True

    return AudienceRangeBar(
        current_user.client,
        field="age",
        ranges=ranges,
        tooltip_formatter=age_formatter,
        key_formatter=key_formatter,
        randomize=randomize,
        solo=solo
    )


def interests(start, end, request_args):
    interests = {
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
    }

    if 'chart' in request_args:
        for k in interests:
            interests[k] += round(random.random() / 4 - 0.125, 2)
            interests[k] = min(interests[k], 1.0)
            interests[k] = max(interests[k], 0.0)

    return DummyHorizontalBarChart('Interests', interests)

def actions(start, end, request_args):
    return DummyHorizontalBarChart('Interests', {
        'Donated to Charity': .42,
        'Attended a Concert': .12,
        'Went on a Vacation': .35,
    })


def hours_active(start, end, request_args):
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
        randomize='chart' in request_args,
    )


def post_performance(start, end, request_args):
    posts = Post.records(current_user.client, "*", 0, 45, ('created_time', 'desc'))
    base_dataset = []
    #INFLUX = init_influxdb()
    for post in reversed(posts.hits):
        ts = time.mktime(datetime.datetime.strptime(post.created_time, date_format).timetuple())
        if ts < end and ts > start:
            base_dataset.append({
                'post_id': post.id,
                'ts': ts*1000,
                'message': current_app.jinja_env.filters['truncate'](post.message, 60),
                #'reach': INFLUX.query("select max(value) from insights.{}.post.{}.post_impressions_unique.lifetime".format(current_user.client._id, post.id))[0]['points'][0][1],
                #'engaged_users': INFLUX.query("select max(value) from insights.{}.post.{}.post_engaged_users.lifetime".format(current_user.client._id, post.id))[0]['points'][0][1],
                'likes': len(post.likes),
                'comments': len(post.comments),
                'shares': post.shares.count if hasattr(post, 'shares') else 0,
            })
        else:
            logging.info("Skipping {}: not between {} and {}".format(ts, start, end))

    views_dataset = []
    engagement_dataset = []
    benchmark_dataset = []
    for post in base_dataset:
        view = post.copy()
        view['value'] = post['likes']

        engage = post.copy()
        engage['value'] = (post['shares'] / float(post['likes'])) if post['likes'] > 0 else 0
        engage['value'] = round(100*engage['value'], 1)
        #engage['value'] = post['likes'] + post['comments'] + post['shares']
        view['engagement'] = engage['value']
        engage['engagement'] = engage['value']


        engagement_dataset.append(engage)
        views_dataset.append(view)

        benchmark_dataset.append({
            'ts': post['ts'],
            'value': 5,
            'engagement': 5,
        })

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
    }

    return DummyDualAxisTimeChart(
        current_user.client,
        comparables,
    )



def share_like_ratios(start, end, request_args):
    return DummyHorizontalBarChart('Share-Fan Ratios (last five posts)', {
        'You': random.random()/10,
        'Greenpeace': random.random()/10,
        'WWF': random.random()/10,
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
