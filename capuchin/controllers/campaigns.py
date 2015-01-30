from flask import Blueprint, render_template
from flask.views import MethodView
from capuchin import config

campaigns = Blueprint(
    'campaigns',
    __name__,
    template_folder=config.TEMPLATES,
)

class CampaignsDefault(MethodView):

    def get(self):
        return render_template("campaigns/index.html")

class CampaignsCreate(MethodView):

    def get(self):
        return render_template("campaigns/create.html")

class CampaignsView(MethodView):

    def get(self):
        return render_template("campaigns/view.html")

campaigns.add_url_rule("/campaigns", view_func=CampaignsDefault.as_view('index'))
campaigns.add_url_rule("/campaigns/create", view_func=CampaignsCreate.as_view('create'))
campaigns.add_url_rule("/campaigns/view", view_func=CampaignsView.as_view('view'))
