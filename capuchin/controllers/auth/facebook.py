from flask import Blueprint, render_template, request, redirect, url_for
from flask.views import MethodView
from flask.ext.login import login_required, current_user
from capuchin import config
from capuchin.models.client import SocialAccount
from flask_oauth import OAuth
import logging
from urlparse import parse_qs, urlparse

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
def get_facebook_token(token=None):
    sa = current_user.social_account(SocialAccount.FACEBOOK)
    return (sa.token, config.FACEBOOK_APP_SECRET)

@facebook.route("/login", methods=['GET', 'POST'])
@login_required
def login():
    return fb_app.authorize(
        callback=url_for('.authorized',
            next=request.args.get('next'), _external=True)
    )

@facebook.route("/authorized", methods=['GET', 'POST'])
@fb_app.authorized_handler
@login_required
def authorized(resp):
    logging.info(resp)
    if resp is None:
        flash("You denied the request", "danger")
        return redirect(url_for(".index"))

    try:
        append = True
        sa = current_user.social_account(account_type=SocialAccount.FACEBOOK)
        if sa.token: append = False
        sa.token = resp.get('access_token')
        if append: current_user.social_accounts.append(sa)
        current_user.save()
        res = fb_app.get(
            "/debug_token",
            data={
                'input_token':resp.get('access_token')
            }
        )
        if res:
            data = res.data.get('data')
            sa.id = data.get("user_id")
            sa.app_id = data.get("app_id")
            [sa.permissions.append(p) for p in data.get("scopes")]
            current_user.save()
            logging.info(current_user.json())
            token = get_long_token(sa.token)
            sa.token = token['token']
            sa.expires = token['expires']
            current_user.save()
            pages = get_pages(sa.id)
    except Exception as e:
        logging.exception(e)

    next_url = request.args.get('next') or url_for('.index')
    current_user.facebook_token = resp['access_token']
    current_user.save()
    return redirect(next_url)

def get_pages(user_id):
    res = fb_app.get("/{}/accounts".format(user_id))
    logging.info(res.data)

def get_long_token(token):
    long_token = fb_app.get(
        "/oauth/access_token",
        data={
            'grant_type':'fb_exchange_token',
            'fb_exchange_token':token,
            'client_id':config.FACEBOOK_APP_ID,
            'client_secret':config.FACEBOOK_APP_SECRET,
        }
    )
    token = parse_qs(long_token.data, keep_blank_values=True)
    return {'token':token.get('access_token', [""])[0], 'expires':token.get('expires', [""])[0]}

class Index(MethodView):
    decorators = [ login_required, ]

    def get(self):
        return render_template("auth/facebook/index.html")


facebook.add_url_rule("/", view_func=Index.as_view('index'))
