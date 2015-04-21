from flask import Blueprint, render_template, redirect, url_for, request
from flask.ext.login import current_user
from flask.views import MethodView

from capuchin import config
from capuchin.models.notification import Notification
from capuchin.models.segment import Segment
from capuchin.views.tables.dashboard import Notifications
from capuchin.controllers.tables import render_table
from capuchin.workers.notifications import get_redirect_url, send_notifications


class NotificationsDefault(MethodView):

    def get(self):
        notifications = render_table(Notifications)
        if not notifications:
            notifications = Notifications(current_user.client).render(
                q='*',
                sort=('created_time', 'desc'),
            )
        return render_template("notifications/index.html", notifications=notifications)


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

        return redirect(url_for("engagement.index"))


notifications = Blueprint(
    'notifications',
    __name__,
    template_folder=config.TEMPLATES,
    url_prefix="/notifications",
)

notifications.add_url_rule("/", view_func=NotificationsDefault.as_view('index'))
notifications.add_url_rule("/save", view_func=NotificationsCreate.as_view('save'))
