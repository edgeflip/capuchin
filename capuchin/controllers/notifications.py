from flask import Blueprint, render_template, redirect, url_for, request
from flask.views import MethodView
from flask.ext.login import current_user
from capuchin import config
from capuchin.models.segment import Segment
from capuchin.models.post import Post
from capuchin.models.notification import Notification

notif = Blueprint(
    'notifications',
    __name__,
    template_folder=config.TEMPLATES,
)

class NotificationsDefault(MethodView):

    def get(self):
        notifications = Notification.find()
        return render_template("notifications/index.html", records=notifications)

class NotificationsCreate(MethodView):

    def get(self):
        posts = Post.records(client=current_user.client)
        messages = [
            "Hey {name}, please give us money!!!",
            "Seriously, {OrgName} will do anything",
            "Checkout this post, you're going to LOVE it!",
        ]
        return render_template("notifications/create.html", segments=Segment.find({'name':{'$ne':None}}), posts=posts, messages=messages)

    def post(self):
        n = Notification()
        n.message = request.form['messages']
        n.client = current_user.client
        segment = Segment(id=request.form['segments'])
        n.segment = segment
        n.post_id = request.form['posts']
        n.smart = True if request.form.get('smart_advertising') else False
        n.save()
        #n.send()
        return redirect(url_for(".index"))

notif.add_url_rule("/notifications", view_func=NotificationsDefault.as_view('index'))
notif.add_url_rule("/notifications/create", view_func=NotificationsCreate.as_view('create'))
notif.add_url_rule("/notifications/save", view_func=NotificationsCreate.as_view('save'))
