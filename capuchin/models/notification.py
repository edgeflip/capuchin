import humongolus as orm
import humongolus.field as field
from capuchin.models.segment import Segment
from capuchin.models.client import Client
from capuchin import config
from flask_oauth import OAuth
import requests

class Notification(orm.Document):
    _db = "capuchin"
    _collection = "notifications"

    message = field.Char()
    segment = field.ModelChoice(type=Segment)
    client = field.DocumentId(type=Client)

    def send(self):
        for i in self.segment.records()['hits']:
            self.logger.info(i)
            self.post(i)

    def post(self, user):
        asid = "10153561577764377"#ASID for Chris Cote for CapuchinDev app, should be None
        for i in user.get('clients', []):
            if str(i.get('id')) == str(self.client._id):
                asid = i.get('asid')
        if asid:
            res = requests.post(
                "https://graph.facebook.com/{}/notifications".format(asid),
                data={
                    "access_token":"{}|{}".format(config.FACEBOOK_APP_ID, config.FACEBOOK_APP_SECRET),
                    "template":self.message,
                    "href":"/test?key=12345",
                    "ref":"test",
                }
            )
            self.logger.info(res.json())
