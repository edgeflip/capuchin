from flask import Blueprint, render_template, redirect, url_for, request
from flask.views import MethodView
from flask.ext.login import current_user
from capuchin import config
from capuchin.models.segment import Segment
from capuchin.models.notification import Notification

notif = Blueprint(
    'notifications',
    __name__,
    template_folder=config.TEMPLATES,
)

class NotificationsDefault(MethodView):

    def get(self):
        return render_template("notifications/index.html")

class NotificationsCreate(MethodView):

    def get(self):
        return render_template("notifications/create.html", Segment=Segment)

    def post(self):
        n = Notification()
        n.message = request.form['message']
        n.client = current_user.client
        segment = Segment(id=request.form['segment'])
        n.segment = segment
        n.save()
        n.send()
        return redirect(url_for("dashboard.index"))

notif.add_url_rule("/notifications", view_func=NotificationsDefault.as_view('index'))
notif.add_url_rule("/notifications/create", view_func=NotificationsCreate.as_view('create'))
notif.add_url_rule("/notifications/save", view_func=NotificationsCreate.as_view('save'))
