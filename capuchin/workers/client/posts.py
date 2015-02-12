from capuchin.app import Capuchin
from capuchin import config
from capuchin import db
from capuchin.insights import POST_INSIGHTS
from flask_oauth import OAuth
import urlparse
import logging
import time
import requests
import datetime
from pprint import pprint
from slugify import slugify

date_format = "%Y-%m-%dT%H:%M:%S+0000"

class ClientPosts():

    def __init__(self, client):
        self.oauth = OAuth()
        self.client = client
        self.INFLUX = db.init_influxdb()
        self.ES = db.init_elasticsearch()
        self.fb_app = self.oauth.remote_app(
            'facebook',
            base_url='https://graph.facebook.com',
            request_token_url=None,
            access_token_url='/oauth/access_token',
            authorize_url='https://www.facebook.com/dialog/oauth',
            consumer_key=config.FACEBOOK_APP_ID,
            consumer_secret=config.FACEBOOK_APP_SECRET,
        )
        self.fb_app.tokengetter(self.get_token)
        self.get_feed()

    def get_token(self):
        return (self.client.facebook_page.token, config.FACEBOOK_APP_SECRET)

    def write_data(self, post):
        p_id = post.get("id")
        post['client'] = str(self.client._id)
        self.ES.index(
            index=config.ES_INDEX,
            doc_type=config.POST_RECORD_TYPE,
            body=post,
            id=p_id
        )
        for i in POST_INSIGHTS:
            points = []
            url = "{}.{}".format(p_id, i)
            data = post.get(i)
            for d in data:
                tm = time.time()
                if d.get("created_time"):
                    tm = time.mktime(time.strptime(d.get("created_time"), date_format))

                points.append((tm, 1, i))
            self.write_influx(points, url)

    def get_feed(self):
        id = self.client.facebook_page.id
        res = self.fb_app.get(
            "/v2.2/{}/feed".format(id),
            data={"limit":250},
        )
        logging.info(res.data)
        for p in res.data.get('data'):
            pprint(p)
            p_id = p.get("id")
            for i in POST_INSIGHTS:
                logging.info("INSIGHT: {}".format(i))
                p[i] = self.page(p_id, i, p.get(i, {}))
                pprint(p[i])
            self.write_data(p)

    def page(self, post_id, typ, data):
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
