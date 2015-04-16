from flask import Blueprint, render_template, redirect, url_for, request
from flask.ext.login import current_user
from flask.views import MethodView

from capuchin import config
from capuchin.models.segment import Segment
from capuchin.models.notification import Notification
from capuchin.workers.notifications import get_redirect_url, send_notifications


class NotificationsDefault(MethodView):

    def get(self):
        notifications = Notification.find()
        return render_template("notifications/index.html", records=notifications)


class NotificationsCreate(MethodView):

    def post(self):
        notification = Notification()
        notification.message = request.form['messages']
        notification.post_id = request.form['posts']
        notification.segment = Segment(id=request.form['segments'])
        notification.smart = bool(request.form.get('smart_advertising'))
        notification.client = current_user.client
        notification.save()

        # Retrieve canvas redirect URL for notification, and send:
        nid = str(notification._id)
        chain = (get_redirect_url.si(nid) | send_notifications.si(nid))
        chain.delay()

        return redirect(url_for(".index"))


notifications = Blueprint(
    'notifications',
    __name__,
    template_folder=config.TEMPLATES,
    url_prefix="/notifications",
)

notifications.add_url_rule("/", view_func=NotificationsDefault.as_view('index'))
notifications.add_url_rule("/save", view_func=NotificationsCreate.as_view('save'))
