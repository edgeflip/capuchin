from flask import Blueprint, render_template, request, redirect, url_for
from capuchin import config
from capuchin.models.list import List
from flask_oauth import OAuth
import logging

oauth = OAuth()

facebook = Blueprint(
    "facebook",
    __name__,
    template_folder=config.TEMPLATES,
    url_prefix="/facebook",
    subdomain=config.AUTH_SUBDOMAIN,
)

fb_app = oauth.remote_app(
    'facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=config.FACEBOOK_APP_ID,
    consumer_secret=config.FACEBOOK_APP_SECRET,
    request_token_params={'scope': 'manage_pages,'}
)

@fb_app.tokengetter
def get_facebook_token():
    return None

@facebook.route("/", methods=['GET', 'POST'])
def index():
    return render_template('auth/facebook/index.html')

@facebook.route("/login", methods=['GET', 'POST'])
def login():
    return fb_app.authorize(
        callback=url_for('.authorized',
            next=request.args.get('next'), _external=True)
    )

@facebook.route("/authorized", methods=['GET', 'POST'])
@fb_app.authorized_handler
def authorized(resp):
    next_url = request.args.get('next') or url_for('dashboard.index')
    if resp is None or 'access_token' not in resp:
        return redirect(next_url)

    logging.info(resp['access_token'])
    return redirect(next_url)
