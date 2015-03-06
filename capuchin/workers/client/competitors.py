from capuchin import db
import logging
import time
from flask_oauth import OAuth


class Competitors():

    def __init__(self, client):
        self.oauth = OAuth()
        self.client = client
        self.INFLUX = db.init_influxdb()
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

    def write_data(self, competitor_id, data):
        datapoint = data.get("likes")
        url = ".".join(["competitors", competitor_id, "lifetime"])
        tm = time.time()
        self.write_influx([(tm, datapoint, "likes")], url)

    def get_token(self):
        return (
            self.client.social.facebook.token,
            self.client.social.facebook.secret
        )

    def spy_on_competitors(self):
        for competitor in self.client.competitors:
            res = self.fb_app.get(
                "/v2.2/{}?fields=likes".format(competitor.id),
            )
            self.write_data(competitor.id, res.data)

    def write_influx(self, points, url):
        data = [
            dict(
                name="insights.{}.{}".format(self.client._id, url),
                columns=["time", "value", "type"],
                points=points
            )
        ]
        try:
            self.INFLUX.write_points(data)
        except Exception as e:
            logging.warning(e)
