from flask import Blueprint, render_template, redirect, url_for, request
from flask.ext.login import current_user
from flask.views import MethodView

from capuchin import config
from capuchin.models.segment import Segment
from capuchin.models.post import Post
from capuchin.models.notification import Notification
from capuchin.workers.notifications import get_redirect_url, send_notifications


class NotificationsDefault(MethodView):

    def get(self):
        notifications = Notification.find()
        return render_template("notifications/index.html", records=notifications)


class NotificationsCreate(MethodView):

    def get(self):
        posts = Post.records(client=current_user.client)
        segment_id = request.args.get('segment')
        post_id = request.args.get('post')
        engage = request.args.get("engage")
        return render_template(
            "notifications/create.html",
            segments=Segment.find({'name': {'$ne': None}}),
            notification={'posts': posts, 'messages': config.MESSAGES},
            segment_id=segment_id,
            post_id=post_id,
            engage=engage,
        )

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
)

notifications.add_url_rule("/notifications", view_func=NotificationsDefault.as_view('index'))
notifications.add_url_rule("/notifications/create", view_func=NotificationsCreate.as_view('create'))
notifications.add_url_rule("/notifications/save", view_func=NotificationsCreate.as_view('save'))
