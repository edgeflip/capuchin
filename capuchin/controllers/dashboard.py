from flask import Blueprint, render_template, request
from flask.views import MethodView
from flask.ext.login import current_user
from capuchin import INFLUX
from capuchin import config
from capuchin.models.list import List
from capuchin.models.segment import Segment
import logging
import json

db = Blueprint(
    'dashboard',
    __name__,
    template_folder=config.TEMPLATES,
)

class InfluxChart(object):

    def __init__(self, client, typ, where="", prefix="insights", date_format="%m/%d/%y"):
        self.client = client
        self.typ = typ
        self.where=where
        self.prefix = prefix
        self.date_format = date_format
        try:
            self.data = self.query()
            self.data = self.massage(self.data)
        except Exception as e:
            logging.exception(e)
            self.data = []

    def query(self): pass
    def massage(self, data):pass
    def dump(self):
        return json.dumps(self.data)

class FBInsightsPieChart(InfluxChart):

    def query(self):
        q = "SELECT sum(value) as value,typ FROM /^{}.{}.{}.*/ {} GROUP BY typ;".format(
            self.prefix,
            self.client._id,
            self.typ,
            self.where
        )
        data = INFLUX.request(
            "db/{0}/series".format(config.INFLUX_DATABASE),
            params={"q":q},
        )
        logging.info(data.status_code)
        return data.json()

    def massage(self, data):
        data = [{
            "label":a['points'][0][2],
            "value":a['points'][0][1]
        } for a in data]
        return data

class FBInsightsMultiBarChart(InfluxChart):

    def query(self):
        res = {}
        for t in self.typ:
            data = INFLUX.request(
                "db/{0}/series".format(config.INFLUX_DATABASE),
                params={'q':
                    "SELECT value FROM {}.{}.{} {};".format(
                        self.prefix,
                        self.client._id,
                        t['type'],
                        self.where
                    )
                }
            )
            res[t['display']] = data.json()
            logging.info(res[t['display']])

        return res

    def massage(self, data):
        ar = []
        for v in data:
            vals = [{"x":a[0], "y":a[2]} for a in data[v][0]['points']]
            vals.reverse()
            ar.append({
                "key":v,
                "values":vals
            })
        return ar;

class HistogramMultiBarChart(InfluxChart):

    def __init__(self, client, typ, where="WHERE time > now()-24h", prefix="insights", date_format="%m/%d/%y %H:%M:00", buckets="1h"):
        self.buckets = buckets
        super(HistogramMultiBarChart, self).__init__(client, typ, where, prefix, date_format)

    def query(self):
        res = {}
        for t in self.typ:
            try:
                data = INFLUX.request(
                    "db/{0}/series".format(config.INFLUX_DATABASE),
                    params={'q':
                        "SELECT count(type) as count FROM {}.{}.{} GROUP BY time({}) fill(0) {};".format(
                            self.prefix,
                            self.client._id,
                            t['type'],
                            self.buckets,
                            self.where,
                        )
                    }
                )
                res[t['display']] = data.json()
            except Exception as e:
                logging.exception(e)
                res[t['display']] = [{"points":[]}]
            logging.info(res[t['display']])

        return res

    def massage(self, data):
        ar = []
        for v in data:
            vals = [{"x":a[0], "y":a[1]} for a in data[v][0]['points']]
            vals.reverse()
            ar.append({
                "key":v,
                "values":vals
            })
        return ar;

class DashboardDefault(MethodView):

    def get(self):

        page_by_type = FBInsightsPieChart(
            current_user.client,
            typ="page_stories_by_story_type",
        )

        engaged_users = FBInsightsMultiBarChart(
            current_user.client,
            [
                {"type":"page_engaged_users", "display":"Engaged Users"},
                {"type":"page_consumptions", "display":"Page Consumptions"},
            ],
            date_format = "%m/%d/%y"
        )

        notifications = HistogramMultiBarChart(
            current_user.client,
            [
                {"type":"notification_sent", "display":"Sent"},
                #{"type":"notification_failure", "display":"Failures"},
            ],
            prefix="events"

        )

        online = FBInsightsPieChart(
            current_user.client,
            "page_fans_online",
        )

        country = FBInsightsPieChart(
            current_user.client,
            typ="page_impressions_by_country_unique",
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
            notifications=notifications
        )

db.add_url_rule("/", view_func=DashboardDefault.as_view('index'))
