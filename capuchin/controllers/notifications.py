from flask import Blueprint, render_template
from flask.views import MethodView
from capuchin import config

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
        return render_template("notifications/create.html")

notif.add_url_rule("/notifications", view_func=NotificationsDefault.as_view('index'))
notif.add_url_rule("/notifications/create", view_func=NotificationsCreate.as_view('create'))
