from capuchin import db
from capuchin import config
import logging
import json

class InfluxChart(object):

    def __init__(self, client, typ, where="", prefix="insights", date_format="%m/%d/%y", massage=True):
        self.INFLUX = db.init_influxdb()
        self.client = client
        self.typ = typ
        self.where=where
        self.prefix = prefix
        self.date_format = date_format
        try:
            self.data = self.query()
            logging.debug(self.data)
            if massage:
                self.data = self.massage(self.data)
                logging.debug(self.data)
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
        logging.debug(q)
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
            logging.debug(q)
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

    def __init__(self, client, typ, where="WHERE time > now()-24h", prefix="insights", date_format="%m/%d/%y %H:%M:00", buckets="1h", massage=True):
        self.buckets = buckets
        super(HistogramChart, self).__init__(client, typ, where, prefix, date_format, massage)

    def query(self):
        res = {}
        for t in self.typ:
            try:
                q = "SELECT sum(value) FROM {}.{}.{} GROUP BY time({}) fill(0) {};".format(
                    self.prefix,
                    self.client._id,
                    t['type'],
                    self.buckets,
                    self.where,
                )
                logging.debug(q)
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
                logging.debug(t['q'])
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


class WordBubble(object):

    def __init__(self, client):
        and_ = [{
            "term": {
                "clients.id": str(client._id)
            }
        }]
        query = {
            "query":{
                "filtered":{"filter":{"and":and_}},
            },
            "aggregations":{
                "words":{
                    "terms":{
                        "field":"top_words.facet",
                        "size":100,
                    }
                }
            }
        }
        ES = db.init_elasticsearch()
        res = ES.search(
            config.ES_INDEX,
            config.USER_RECORD_TYPE,
            size=0,
            _source=False,
            body=query
        )
        logging.debug(res)
        self.data = {"name":"Words", "children":[]}
        for i in res['aggregations']['words']['buckets']:
            logging.debug(i)
            self.data['children'].append({
                "name":i['key'],
                "size":i['doc_count']
            })

    def dump(self):
        return json.dumps(self.data)

class HorizontalBarChart(object):

    def __init__(self, client, facet):
        and_ = [{
            "term": {
                "clients.id": str(client._id)
            }
        }]
        query = {
            "query":{
                "filtered":{"filter":{"and":and_}},
            },
            "aggregations":{
                facet:{
                    "terms":{
                        "field":"{}.facet".format(facet),
                        "size":10,
                    }
                }
            }
        }
        ES = db.init_elasticsearch()
        res = ES.search(
            config.ES_INDEX,
            config.USER_RECORD_TYPE,
            size=0,
            _source=False,
            body=query
        )
        logging.debug(res)
        self.data = {"key":facet, "values":[]}
        for i in res['aggregations'][facet]['buckets']:
            self.data['values'].append({
                "label":i['key'],
                "value":i['doc_count']
            })

        self.data = [self.data]

    def dump(self):
        return json.dumps(self.data)
