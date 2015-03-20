from capuchin import config
from capuchin import db
from capuchin.views.insights import POST_INSIGHTS
from flask_oauth import OAuth
import logging
import time
import datetime
import random

date_format = "%Y-%m-%dT%H:%M:%S+0000"

class PullNonClientPosts():

    def __init__(self, client, page_id, since):
        self.oauth = OAuth()
        self.client = client
        self.page_id = page_id
        self.since = since
        self.INFLUX = db.init_influxdb()
        self.ES = db.init_elasticsearch()
        self.fb_app = self.oauth.remote_app(
            'facebook',
            base_url='https://graph.facebook.com',
            request_token_url=None,
            access_token_url='/oauth/access_token',
            authorize_url='https://www.facebook.com/dialog/oauth',
            consumer_key=client.social.facebook.app_id,
            consumer_secret=client.social.facebook.secret,
        )
        self.fb_app.tokengetter(self.get_token)
        self.get_feed()

    def get_token(self):
        return (self.client.social.facebook.token, self.client.social.facebook.secret)

    def get_count(self, url):
        name = "insights.{}.post.{}".format(self.client._id, url)
        q = "select count(type) from {}".format(name)
        try:
            res = self.INFLUX.query(q)
            return res[0]['points'][0][1]
        except Exception as e:
            logging.warn(e)
            return None


    def write_data(self, post):
        p_id = post.get("id")
        post['client'] = str(self.client._id)
        self.ES.index(
            index=config.ES_INDEX,
            doc_type=config.POST_RECORD_TYPE,
            body=post,
            id=p_id
        )
        num_hours = 48
        created_time = datetime.datetime.strptime(post.get('created_time'), date_format)
        shares = post.get("shares", {}).get("count", 0)
        if shares > 0:
            distribution = reversed(sorted([random.expovariate(1/(float(shares)/num_hours)) for x in range(0,num_hours)]))
            for hours_forward, value in enumerate(distribution):
                if int(value) == 0:
                    continue
                tm = time.mktime((created_time + datetime.timedelta(hours=hours_forward)).timetuple())
                self.write_influx([(tm, int(value), 'shares')], url="{}.{}".format(p_id, "shares"))

        likes = post.get('likes', [])
        num_likes = len(likes)
        if num_likes > 0:
            distribution = reversed(sorted([random.expovariate(1/(float(num_likes)/num_hours)) for x in range(0,num_hours)]))
            for hours_forward, value in enumerate(distribution):
                if int(value) == 0:
                    continue
                tm = time.mktime((created_time + datetime.timedelta(hours=hours_forward)).timetuple())
                self.write_influx([(tm, int(value), 'likes')], url="{}.{}".format(p_id, "likes"))

        tm = time.time()
        for i in ['comments', 'attachments']:
            url = "{}.{}".format(p_id, i)
            count = self.get_count(url)
            points = [(time.time(), 0, i)] if count == None else []
            data = post.get(i)
            for d in data[count:]:
                ct = d.get("created_time")
                if ct:
                    tm = time.mktime(time.strptime(d.get("created_time"), date_format))
                else:
                    tm = time.time()

                points.append((tm, 1, i))

            self.write_influx(points, url)

    def get_feed(self):
        id = self.page_id
        data = {"limit":250}
        since = time.mktime(self.since.timetuple())
        data['until'] = int(time.time())
        while data['until'] > since:
            print "trying ", data
            res = self.fb_app.get(
                "/v2.2/{}/feed".format(id),
                data=data,
            )

            for p in res.data.get('data'):
                fro = p.get("from")
                if fro.get("id") != str(self.page_id):
                    continue
                p_id = p.get("id")
                for i in POST_INSIGHTS:
                    p[i] = self.page_interactions(p_id, i, p.get(i, {}))
                self.write_data(p)
                post_time = time.mktime(datetime.datetime.strptime(p.get("created_time"), date_format).timetuple())
                if post_time <= data['until']:
                    data['until'] = post_time

    def page_interactions(self, post_id, typ, data):
        res = [a for a in data.get("data", [])]
        cursors = data.get("paging", {}).get("cursors", {})
        if cursors.get('before') == cursors.get('after'): return res
        last = {'before':cursors['before'], 'after':cursors['after']}
        for i in last:
            while last[i]:
                resp = self.fb_app.get(
                    "/v2.2/{}/{}".format(post_id, typ),
                    data={
                        "limit":250,
                        i:cursors[i]
                    },
                )
                res+=[a for a in resp.data.get("data")]
                af = resp.data.get("paging", {}).get(i)
                last[i] = af if af != last[i] else None

        return res

    def write_influx(self, points, url):
        data = [
            dict(
                name = "insights.{}.post.{}".format(self.client._id, url),
                columns = ["time", "value", "type"],
                points = points
            )
        ]
        logging.info("Writing: {}".format(data))
        try:
            res = self.INFLUX.write_points(data)
            logging.info(res)
        except Exception as e:
            logging.warning(e)
