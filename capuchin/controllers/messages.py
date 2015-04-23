from flask import Blueprint
from flask.ext.login import current_user
from flask.views import MethodView
from capuchin import config
import datetime

message = Blueprint(
    'messages',
    __name__,
    template_folder=config.TEMPLATES,
    url_prefix="/messages",
)

class MarkAsRead(MethodView):

    def post(self):
        for message in current_user.client.messages(query={"read": None}):
            message.read = datetime.datetime.utcnow()
            message.save()
        return ''

message.add_url_rule("/mark_read", view_func=MarkAsRead.as_view('mark_read'))
