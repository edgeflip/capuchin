import datetime
import logging
import time

import requests
from flask_oauth import OAuth
from slugify import slugify

from capuchin import db


DATE_FORMAT = "%Y-%m-%dT%H:%M:%S+0000"


class Insights():

    def __init__(self, client, id, since, typ=None):
        self.oauth = OAuth()
        self.id = id
        self.type = typ
        self.client = client
        self.since = since
        self.INFLUX = db.init_influxdb()
        logging.debug(client.social.facebook._json())
        self.fb_app = self.oauth.remote_app(
            'facebook',
            base_url='https://graph.facebook.com/',
            request_token_url=None,
            access_token_url='/oauth/access_token',
            authorize_url='https://www.facebook.com/dialog/oauth',
            consumer_key=client.social.facebook.app_id,
            consumer_secret=client.social.facebook.secret,
        )
        self.fb_app.tokengetter(self.get_token)
        self.get_insights()

    def get_token(self):
        return (self.client.social.facebook.token, self.client.social.facebook.secret)

    def write_data(self, record):
        for insight in record.get('data', ()):
            period = insight.get("period")
            if period != 'day' and period != 'lifetime':
                continue

            name = insight['name']
            url = '{}.{}'.format(name, period)
            if self.type:
                url = '{}.{}.{}'.format(self.type, self.id, url)

            points = []
            for event in insight.get('values', ()):
                value = event.get('value')
                if not value:
                    continue

                end_time = event.get('end_time')
                tm = time.mktime(time.strptime(end_time, DATE_FORMAT)) if end_time else time.time()

                if isinstance(value, dict):
                    points.extend((tm, value1, slugify(key1))
                                  for (key1, value1) in value.iteritems())
                else:
                    points.append((tm, value, name))

            if points:
                self.write_influx(points, url)

    def get_insights(self):
        id = self.id
        data = {}
        data['since'] = time.mktime(self.since.timetuple())
        data['until'] = time.mktime(datetime.datetime.utcnow().timetuple())
        res = self.fb_app.get('/v2.2/{}/insights'.format(id), data=data)
        self.write_data(res.data)
        self.page(res.data)

    def page(self, data):
        next_ = data.get('paging', {}).get('next')
        last = next_
        while next_:
            response = requests.get(next_)
            data = response.json()
            self.write_data(data)
            next_ = data.get('paging', {}).get('next')
            if next_ == last:
                next_ = None
            else:
                last = next_

    def write_influx(self, points, url):
        data = [
            {
                'name': 'insights.{}.{}'.format(self.client._id, url),
                'columns': ['time', 'value', 'type'],
                'points': points,
            }
        ]
        logging.debug("Writing: {}".format(data))
        try:
            res = self.INFLUX.write_points(data)
            logging.debug(res)
        except Exception as exc:
            logging.warning(exc, exc_info=True)
