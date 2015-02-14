from capuchin import db
from capuchin import config
import logging
import json

class InfluxChart(object):

    def __init__(self, client, typ, where="", prefix="insights", date_format="%m/%d/%y"):
        self.INFLUX = db.init_influxdb()
        self.client = client
        self.typ = typ
        self.where=where
        self.prefix = prefix
        self.date_format = date_format
        try:
            self.data = self.query()
            logging.info(self.data)
            self.data = self.massage(self.data)
            logging.info(self.data)
        except Exception as e:
            logging.exception(e)
            self.data = []

    def query(self): pass
    def massage(self, data):pass
    def dump(self):
        return json.dumps(self.data)

class FBInsightsPieChart(InfluxChart):

    def query(self):
        q = "SELECT sum(value), type FROM {}.{}.{} {} GROUP BY type;".format(
            self.prefix,
            self.client._id,
            self.typ,
            self.where
        )
        logging.info(q)
        data = self.INFLUX.request(
            "db/{0}/series".format(config.INFLUX_DATABASE),
            params={"q":q},
        )
        return data.json()

    def massage(self, data):
        data = [{
            "label":a[2],
            "value":a[1]
        } for a in data[0]['points']]
        return data

class FBInsightsMultiBarChart(InfluxChart):

    def query(self):
        res = {}
        for t in self.typ:
            q = "SELECT value FROM {}.{}.{} {};".format(
                self.prefix,
                self.client._id,
                t['type'],
                self.where
            )
            logging.info(q)
            data = self.INFLUX.request(
                "db/{0}/series".format(config.INFLUX_DATABASE),
                params={'q':q}
            )
            res[t['display']] = data.json()

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

class HistogramChart(InfluxChart):

    def __init__(self, client, typ, where="WHERE time > now()-24h", prefix="insights", date_format="%m/%d/%y %H:%M:00", buckets="1h"):
        self.buckets = buckets
        super(HistogramChart, self).__init__(client, typ, where, prefix, date_format)

    def query(self):
        res = {}
        for t in self.typ:
            try:
                q = "SELECT sum(value) FROM {}.{}.{} GROUP BY time({}), type fill(0) {};".format(
                    self.prefix,
                    self.client._id,
                    t['type'],
                    self.buckets,
                    self.where,
                )
                logging.info(q)
                data = self.INFLUX.request(
                    "db/{0}/series".format(config.INFLUX_DATABASE),
                    params={'q':q}
                )
                res[t['display']] = data.json()
            except Exception as e:
                res[t['display']] = [{"points":[]}]

        return res

    def massage(self, data):
        ar = []
        for v in data:
            try:
                vals = [{"x":a[0], "y":a[1]} for a in data[v][0]['points']]
                vals.reverse()
                ar.append({
                    "key":v,
                    "values":vals
                })
            except:pass

        return ar;

class FreeHistogramChart(HistogramChart):

    def query(self):
        res = {}
        for t in self.typ:
            try:
                logging.info(t['q'])
                data = self.INFLUX.request(
                    "db/{0}/series".format(config.INFLUX_DATABASE),
                    params={'q':t['q'].format(self.client._id)}
                )
                t['values'] = data.json()
                res[t['display']] = t
            except Exception as e:
                t['values'] = [{'points':[]}]
                res[t['display']] = t

        return res

    def massage(self, data):
        ar = []
        def get(l, i, o_i):
            try:
                return l[i]
            except:
                return l[o_i]
        for v in data:
            try:
                vals = [{"x":a[0], "y":get(a, 2, 1)} for a in data[v]["values"][0]['points']]
                vals.reverse()
                obj = {
                    "key":v,
                    "values":vals,
                }
                if data[v].get("kwargs"):
                    obj.update(data[v].get("kwargs"))
                ar.append(obj)
            except Exception as e:
                logging.exception(e)

        return ar;