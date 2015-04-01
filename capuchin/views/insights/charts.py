from capuchin import db
from capuchin import config
from capuchin.models.city import City
import logging
import json
import random
import time
import datetime

class InfluxChart(object):

    def __init__(self, client, typ, where="", prefix="insights", date_format="%m/%d/%y", massage=True, tooltip_formatter=None, randomize=False):
        self.INFLUX = db.init_influxdb()
        self.client = client
        self.typ = typ
        self.where=where
        self.prefix = prefix
        self.date_format = date_format
        self.tooltip_formatter = tooltip_formatter
        self.randomize = randomize
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


class FBInsightsDiscreteBarChart(InfluxChart):

    def query(self):
        q = "SELECT mean(value), type FROM {}.{}.{} {} GROUP BY type;".format(
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
        tooltips = {}
        values = []
        for a in data[0]['points']:
            y = a[1]
            if self.randomize:
                y += random.randint(int(-y/5), int(y/5))
            x = a[2]
            tooltips[x] = self.tooltip_formatter(x, y)
            values.append({
                "label":x,
                "value":y
            })

        values = sorted(values, key=lambda x: int(x['label']))
        data = [{
            "key": "Stuff",
            "values": values
        }]
        return {"points": data, "messages": tooltips}


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
        return ar


class DummyDualAxisTimeChart(InfluxChart):

    def massage(self, data):
        #logging.info(data)
        ar = []

        tooltips = {}
        for v, d in data.iteritems():
            key = "{} (right axis)".format(v) if self.typ[v]['yAxis'] == 2 else v
            tooltips[key] = {}
            vals = [
                {"x":a['ts'], "y":a['value'], "message": a.get('message', None), "likes": a.get('likes', 0), "engagement": a.get('engagement', 0)}
                for a in d
            ]
            vals.reverse()
            for i, val in enumerate(vals):
                pretty_date = datetime.datetime.strftime(datetime.datetime.fromtimestamp(val["x"]/1000), self.date_format)
                if val['message']:
                    tooltips[key][i] = "<div class='overhead-popover'>" + "<br />".join([val['message'], pretty_date, "Likes: {}".format(val['likes']), "Engagement: {}%".format(val['engagement'])]) + "</div>";
                else:
                    tooltips[key][i] = "<div class='overhead-popover'>" + "<br />".join([pretty_date, "{}: {}".format(key, val['y'])]) + "</div>"

            ar.append({
                "key":v,
                "values":vals,
                "yAxis": self.typ[v]['yAxis'],
                "type": self.typ[v]['type'],
                "color": self.typ[v]['color'],
            })
        return {"points": ar, "messages": tooltips}

    def query(self):
        res = {}
        for display_name, info in self.typ.iteritems():
            res[display_name] = info['data']
        return res


class DummySparklineChart(InfluxChart):

    def massage(self, data):
        logging.info(data)
        points = [{"x":a['ts'], "y":a['value']} for a in data]
        return points

    def query(self):
        return self.typ

class DualAxisTimeChart(InfluxChart):

    def __init__(self, client, typ, start=None, end=None, buckets='1d', **kwargs):
        self.start = start or int(time.time()) - 86400*30
        self.end = min(end, int(time.time()))
        self.buckets = buckets
        where = "time > {}s and time < {}s".format(self.start, self.end)
        super(DualAxisTimeChart, self).__init__(client, typ, where, **kwargs)

    def massage(self, data):
        logging.info(data)
        ar = []

        tooltips = {}
        for v, d in data.iteritems():
            key = "{} (right axis)".format(v) if self.typ[v]['yAxis'] == 2 else v
            tooltips[key] = {}
            if len(d) == 0 or 'points' not in d[0]:
                continue
            vals = [
                {"x":a[0], "y":a[1]}
                for a in d[0]['points']
            ]
            vals.reverse()
            for i, val in enumerate(vals):
                pretty_date = datetime.datetime.strftime(datetime.datetime.fromtimestamp(val["x"]/1000), self.date_format)
                tooltips[key][i] = "<div class='overhead-popover'>" + "<br />".join([pretty_date, "{}: {}".format(key, val['y'])]) + "</div>"
            ar.append({
                "key":v,
                "values":vals,
                "yAxis": self.typ[v]['yAxis'],
                "type": self.typ[v]['type'],
                "color": self.typ[v]['fill_color'],
                "stroke_color": self.typ[v].get('stroke_color', ''),
            })
        logging.info(tooltips)
        return {"points": ar, "messages": tooltips}

    def query(self):
        res = {}
        for display_name, info in self.typ.iteritems():
            series = info['series'].format(self.client._id)
            query = "select time, max(value) from {} where {} group by time({})".format(series, self.where, self.buckets)
            logging.info(query)

            data = self.INFLUX.request(
                "db/{0}/series".format(config.INFLUX_DATABASE),
                params={'q':query}
            )

            res[display_name] = data.json()
        return res

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


class SeriesGrowthComparisonChart(FreeHistogramChart):

    def __init__(self, client, typ, start, end, where="", **kwargs):
        self.start = start or int(time.time()) - 172800
        self.end = end or int(time.time())
        super(SeriesGrowthComparisonChart, self).__init__(client, typ, where, **kwargs)

    def massage(self, results):
        return results

    def query(self):
        pretty_dt = datetime.datetime.fromtimestamp(self.start).strftime(self.date_format)
        results = {"key": "Percent Growth since {}".format(pretty_dt), "values": []}
        for definition in self.typ:
            logging.info(definition)
            definition['series'] = definition['series'].format(self.client._id)
            end_query = """
                select
                    value
                from
                    {}
                where time < {}s
                limit 1
            """.format(definition['series'], self.end)
            logging.info(end_query)
            end_data = self.INFLUX.request(
                "db/{0}/series".format(config.INFLUX_DATABASE),
                params={'q':end_query}
            ).json()

            if len(end_data) > 0:
                end_value = end_data[0]['points'][0][2]
            else:
                end_value = 0

            start_query = """
                select
                    value
                from
                    {}
                where time < {}s
                limit 1
            """.format(definition['series'], self.start)
            logging.info(start_query)
            start_data = self.INFLUX.request(
                "db/{0}/series".format(config.INFLUX_DATABASE),
                params={'q':start_query}
            ).json()
            if len(start_data) > 0:
                start_value = start_data[0]['points'][0][2]
            else:
                start_value = 0

            logging.info("start value={}".format(start_value))
            logging.info("end value={}".format(end_value))
            if start_value == 0 or end_value == 0:
                rate_of_change = 0
            else:
                rate_of_change = (end_value - start_value) / float(start_value)
            results['values'].append({
                "label": definition["display"],
                "value": rate_of_change*100
            })

        logging.info(results)
        return [results]


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
                        "field":"likes.name.facet",
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


class DummyPieChart(object):
    def __init__(self, title, data, date_format=None):
        self.title = title
        self.date_format = date_format
        mean = sum(data.values())
        self.data = [{"label": k, "value": v, "percent": "{0:.0f}%".format(100*(float(v)/mean))} for k, v in data.iteritems()]

    def dump(self):
        return json.dumps(self.data)


class DummyBarChart(object):
    def __init__(self, title, data, date_format=None, tooltip_formatter=None):
        self.title = title
        self.date_format = date_format
        self.tooltip_formatter = tooltip_formatter
        tooltips = {}
        values = []
        for x, y in data:
            tooltips[x] = self.tooltip_formatter(x, y)
            values.append({
                "label":x,
                "value":y
            })

        data = [{
            "key": "Stuff",
            "values": values
        }]
        self.data = {"points": data, "messages": tooltips}

    def dump(self):
        return json.dumps(self.data)


class DummyHorizontalBarChart(object):
    def __init__(self, title, data, date_format=None):
        self.date_format=date_format
        self.title = title
        values = [{"label": k, "value": v} for k, v in data.iteritems()]
        values = sorted(values, key=lambda row: -row['value'])
        self.data = [{
            "key": self.title,
            "values": values
        }]

    def dump(self):
        return json.dumps(self.data)


#class DummyBarChart(object):

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

class TopCities(object):

    def __init__(self, client, top_n, cities_override):
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
                "cities":{
                    "terms":{
                        "script":"doc['location_name.city.facet'].value+','+doc['location_name.state.facet'].value",
                        "size":top_n,
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
        logging.info(res)
        values = []
        for i in res['aggregations']['cities']['buckets']:
            logging.debug(i)
            city, state = i['key'].split(",")
            if city:
                c = City.find_one({"full_state": state, "city": city})
                if c:
                    val = i['doc_count']
                    values.append({
                        "label":"{}, {}".format(c.city, c.state),
                        "value": i['doc_count']
                    })
        if cities_override:
            total = sum(val['value'] for val in values)
            for val in values:
                val['value'] *= float(val['value'])/total
                val['value'] = max(int(val['value']), 1)
        self.data = [{
            'key': 'Top Cities',
            'values':values
        }]

    def dump(self):
        return json.dumps(self.data)


class AudienceRangeBar(object):
    def __init__(self,
        client,
        field,
        ranges,
        tooltip_formatter,
        key_formatter,
        randomize=False,
        solo=None,
    ):
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
                "agg":{
                    "range":{
                        "field":field,
                        "ranges":ranges,
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
        logging.info(res)
        self.tooltip_formatter = tooltip_formatter
        self.key_formatter = key_formatter
        tooltips = {}
        values = []
        for i in res['aggregations']['agg']['buckets']:
            x = self.key_formatter(i['key'])
            y = i['doc_count']
            if randomize and y > 20:
                y += random.randint(-20, 20)
            if solo and x != solo:
                y = 0
            tooltips[x] = self.tooltip_formatter(x, y)
            values.append({
                'label': x,
                'value': y,
            })

        data = [{
            "key": "",
            "values": values
        }]
        self.data = {"points": data, "messages": tooltips}

    def dump(self):
        return json.dumps(self.data)


class AudiencePie(object):

    def __init__(self, client, field):
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
                "agg":{
                    "terms":{
                        "field":field,
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
        logging.info(res)
        raw_data = res['aggregations']['agg']['buckets']
        total = sum(i['doc_count'] for i in raw_data)
        self.data = [{
            'label': i['key'],
            'value': i['doc_count'],
            'percent': "{0:.0f}%".format(100*(float(i['doc_count'])/total))
        } for i in raw_data]


    def dump(self):
        return json.dumps(self.data)
