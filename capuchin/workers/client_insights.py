from capuchin import Capuchin
from capuchin import config
from capuchin import INFLUX
from flask_oauth import OAuth
import logging
import time

date_format = "%Y-%m-%dT%H:%M:%S+0000"

class ClientInsights():

    INSIGHTS = [
        "page_stories",
        "page_stories_by_story_type",
        "page_storytellers",
        "page_storytellers_by_story_type",
        "page_storytellers_by_age_gender",
        "page_storytellers_by_city",
        "page_storytellers_by_country",
        "page_storytellers_by_locale",
        "page_impressions",
        "page_impressions_unique",
        "page_impressions_paid",
        "page_impressions_paid_unique",
        "page_impressions_organic",
        "page_impressions_organic_unique",
        "page_impressions_viral",
        "page_impressions_viral_unique",
        "page_impressions_by_story_type",
        "page_impressions_by_story_type_unique",
        "page_impressions_by_city_unique",
        "page_impressions_by_country_unique",
        "page_impressions_by_locale_unique",
        "page_impressions_by_age_gender_unique",
        "page_impressions_frequency_distribution",
        "page_impressions_viral_frequency_distribution",
        "page_impressions_by_paid_non_paid",
        "page_impressions_by_paid_non_paid_unique",
        "page_engaged_users",
        "page_consumptions",
        "page_consumptions_unique",
        "page_consumptions_by_consumption_type",
        "page_consumptions_by_consumption_type_unique",
        "page_places_checkin_total",
        "page_places_checkin_total_unique",
        "page_places_checkin_mobile",
        "page_places_checkin_mobile_unique",
        "page_places_checkins_by_age_gender",
        "page_places_checkins_by_locale",
        "page_places_checkins_by_country",
        "page_negative_feedback",
        "page_negative_feedback_unique",
        "page_negative_feedback_by_type",
        "page_negative_feedback_by_type_unique",
        "page_positive_feedback_by_type",
        "page_positive_feedback_by_type_unique",
        "page_fans_online",
        "page_fans_online_per_day",
        "page_fans",
        "page_fans_locale",
        "page_fans_city",
        "page_fans_country",
        "page_fans_gender_age",
        "page_fan_adds",
        "page_fan_adds_unique",
        "page_fans_by_like_source",
        "page_fans_by_like_source_unique",
        "page_fan_removes",
        "page_fan_removes_unique",
        "page_fans_by_unlike_source_unique",
        "page_posts_impressions",
        "page_posts_impressions_unique",
        "page_posts_impressions_paid",
        "page_posts_impressions_paid_unique",
        "page_posts_impressions_organic",
        "page_posts_impressions_organic_unique",
        "page_posts_impressions_viral",
        "page_posts_impressions_viral_unique",
        "page_posts_impressions_frequency_distribution",
        "page_posts_impressions_by_paid_non_paid",
        "page_posts_impressions_by_paid_non_paid_unique",
    ]

    def __init__(self, client):
        self.oauth = OAuth()
        self.client = client
        self.fb_app = self.oauth.remote_app(
            'facebook',
            base_url='https://graph.facebook.com/',
            request_token_url=None,
            access_token_url='/oauth/access_token',
            authorize_url='https://www.facebook.com/dialog/oauth',
            consumer_key=config.FACEBOOK_APP_ID,
            consumer_secret=config.FACEBOOK_APP_SECRET,
        )
        self.fb_app.tokengetter(self.get_token)
        self.get_insights()

    def get_token(self):
        return (self.client.facebook_page.token, config.FACEBOOK_APP_SECRET)

    def get_insights(self):
        id = self.client.facebook_page.id
        for i in self.INSIGHTS:
            res = self.fb_app.get(
                "/v2.2/{}/insights/{}".format(id, i),
                data={"period":"day"}
            )
            logging.info(res.data)
            for insight in res.data.get("data", []):
                name = insight.get("name")
                for event in insight.get("values"):
                    tm = time.mktime(time.strptime(event.get("end_time"), date_format))

                    val = event.get("value")
                    if isinstance(val, dict):
                        for k,v in val.iteritems():
                            t = "{}.{}".format(name, "-".join(k.split(" ")))
                            self.write_influx((tm, v, t))
                    else:
                        self.write_influx((tm, val, name))


    def write_influx(self, event):
        time, val, typ = event
        data = [
            dict(
                name = "insights.{}.{}".format(self.client._id, typ),
                columns = ["time", "value", "typ"], #typ is probably redundant cause it's in the name
                points = [[time, val, typ]]
            )
        ]
        logging.info("Writing: {}".format(data))
        try:
            res = INFLUX.write_points(data)
            logging.info(res)
        except Exception as e:
            logging.warning(e)
