from flask.views import MethodView
from flask import Blueprint

frontend = Blueprint(
    'frontend',
    __name__,
)

class Catchall(MethodView):

    def get(self): pass
    def post(self): pass


frontend.add_url_rule("/../auth/token/<token>", view_func=Catchall.as_view('token'))
frontend.add_url_rule("/../auth/facebook/login", view_func=Catchall.as_view('facebook_login'))
