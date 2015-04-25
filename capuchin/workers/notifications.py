import datetime
import requests

from celery.utils.log import get_task_logger

from capuchin import config
from capuchin.integration import chapo
from capuchin.workers import app
from capuchin.models.event import record_event
from capuchin.models.notification import Notification
from capuchin.models.segment import Segment
from capuchin.models.user import User


LOG = get_task_logger(__name__)


@app.task
def get_redirect_url(nid):
    notification = Notification(id=nid)
    url = notification.get_url()
    LOG.debug("Notification target URL: %s", url)
    location = chapo.get_redirect_url(url)
    (_base, path) = location.split('/canvas/', 1)
    LOG.debug("Notification redirect href: %s", path)
    notification.redirect.original_url = url
    notification.redirect.url = location
    notification.redirect.path = path
    notification.save()


@app.task
def send_notifications(nid):
    notification = Notification(id=nid)

    # Raise formatting errors eagerly:
    formatted = notification.message.format(
        Name="@[{fbid}]",
        Org=notification.client.name,
    )

    for user in notification.segment.records().hits:
        send_notification.delay(nid, user.efid, formatted)

    segment = Segment(id=notification._get('segment')._value)
    segment.last_notification = datetime.datetime.utcnow()
    segment.save()


class NotificationError(Exception):
    pass


class UnaffiliatedUserError(NotificationError):
    pass


# DEMO
class UnauthorizedDemo(NotificationError):

    # FIXME: db apparently loaded legacy fbids in place of app-scoped
    # (and these were merely fixed in place)
    WHITELIST = {
        100009535770088, # Jed 'One-Take' Bartlet, test user of SociallyMinded app
        10100552502193000, # Jesse
        10153076992186411, # Rayid
        10102646865542260, # Tristan
    }


@app.task
def send_notification(nid, efid, template):
    notification = Notification(id=nid)
    user = User(id=efid)

    client = notification.client
    for user_client in user.get('clients', []):
        user_client_id = user_client.get('id')
        asid = user_client.get('asid')
        if user_client_id and asid and str(user_client_id) == str(client._id):
            break
    else:
        raise UnaffiliatedUserError("User {} not affiliated with client {} of notification {}"
                                    .format(efid, client._id, nid))

    # DEMO
    if asid not in UnauthorizedDemo.WHITELIST:
        raise UnauthorizedDemo("User {} (efid {}) is not approved to receive demo notifications"
                               .format(asid, efid))

    # FIXME: appid not global, comes from user-client
    try:
        response = requests.post(
            'https://graph.facebook.com/{}/notifications'.format(asid),
            data={
                'access_token': '{}|{}'.format(config.FACEBOOK_APP_ID, config.FACEBOOK_APP_SECRET),
                'template': template.format(fbid=asid),
                'href': notification.redirect.path,
                'ref': 'demo',
            }
        )
        response.raise_for_status()
    except (IOError, RuntimeError) as exc:
        if isinstance(exc, requests.HTTPError) and 400 <= exc.response.status_code < 500:
            LOG.fatal("send_notification to user %s (efid %s) failed with %r | %r",
                      asid, efid, exc, exc.response.content)
            raise

        send_notification.retry(exc=exc)

    user.last_notification = datetime.datetime.utcnow()
    User.save(data=user)

    result = response.json()
    event_type = 'notification_sent' if result.get('success') else 'notification_failure'
    record_event(client, event_type, value=1, user=asid, notification=str(notification._id))
