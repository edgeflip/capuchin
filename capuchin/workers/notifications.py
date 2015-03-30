from capuchin import config
from capuchin.workers import app
from capuchin.models.notification import Notification
import datetime
import requests
import logging


@app.task
def get_redirect_url(nid):
    notification = Notification(id=nid)
    url = notification.get_url()
    logging.info("URL: {}".format(url))
    res = requests.post(
        config.REDIRECTOR_URL,
        data={'url': url},
        headers={'Authorization': ' apikey {}'.format(config.REDIRECTOR_AUTH)},
        allow_redirects=False
    )
    path = "/{}".format("/".join(res.headers.get("location").split("/")[-4:]))
    logging.info("Redirect Location: {}".format(path))
    notification.redirect.original_url = url
    notification.redirect.url = res.headers.get("location")
    notification.redirect.path = path
    notification.save()


@app.task
def send_notifications(nid):
    notification = Notification(id=nid)
    for i in notification.segment.records().hits:
        try:
            logging.info(i)
            notification.post(i)
        except Exception as e:
            logging.exception(e)

    seg = Segment(id=notification._get('segment')._value)
    seg.last_notification = datetime.datetime.utcnow()
    seg.save()
