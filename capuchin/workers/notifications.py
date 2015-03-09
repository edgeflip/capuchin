from capuchin import config
from capuchin.workers import app
from capuchin.models.notification import Notification
import datetime
import requests
import logging

@app.task
def get_redirect_url(notification):
    notif = Notification(id=notification)
    url = notif.get_url()
    logging.info("URL: {}".format(url))
    res = requests.post(
        config.REDIRECTOR_URL,
        data={'url':url},
        headers={'Authorization':' apikey {}'.format(config.REDIRECTOR_AUTH)},
        allow_redirects=False
    )
    path = "/{}".format("/".join(res.headers.get("location").split("/")[-4:]))
    logging.info("Redirect Location: {}".format(path))
    notif.redirect.original_url = url
    notif.redirect.url = res.headers.get("location")
    notif.redirect.path = path
    notif.save()

@app.task
def send_notifications(notif):
    notif = Notification(id=notif)
    for i in notif.segment.records().hits:
        try:
            logging.info(i)
            notif.post(i)
        except Exception as e:
            logging.exception(e)

    seg = Segment(id=notif._get('segment')._value)
    seg.last_notification = datetime.datetime.utcnow()
    seg.save()
