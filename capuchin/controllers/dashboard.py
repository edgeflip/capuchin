from flask import Blueprint, render_template, request, jsonify
from flask.ext.login import current_user
from flask.views import MethodView

from capuchin import config
from capuchin.controllers.tables import render_table
from capuchin.views import insights
from capuchin.views.tables.dashboard import Posts


db = Blueprint(
    'dashboard',
    __name__,
    template_folder=config.TEMPLATES,
)


class DashboardDefault(MethodView):

    def get(self):
        posts = render_table(Posts)
        if not posts:
            posts = Posts(current_user.client).render(size=5,
                                                      pagination=False,
                                                      sort=('created_time', 'desc'))

        try:
            like_change = insights.like_weekly_change()
            engagement_change = insights.engagement_weekly_change()
        except:
            like_change = {'change': 0, 'total': 0}
            engagement_change = {'change': 0, 'total': 0}

        return render_template(
            "dashboard/index.html",
            posts=posts,
            like_change=like_change,
            engagement_change=engagement_change,
        )


class DashboardChart(MethodView):

    charts = {
        "page_by_type": insights.page_by_type,
        "engaged_users": insights.engaged_users,
        "country": insights.country,
        "online": insights.online,
        "notifications": insights.notifications,
        'post_reach': insights.post_reach,
        "likes": insights.likes,
        "like_gains": insights.like_gains,
        "city_population": insights.city_population,
        "referrers": insights.referrers,
        "top_words": insights.top_words,
        "top_likes": insights.top_likes,
        "total_growth_over_time": insights.growth_over_time,
    }

    def get(self, chart_id):
        start_ts = request.args.get("start_ts", None)
        end_ts = request.args.get("end_ts", None)
        res = self.charts[chart_id](start=start_ts, end=end_ts, request_args=request.args)
        obj = {'data': res.data}
        try:
            obj['date_format'] = res.date_format
        except:
            pass
        return jsonify(**obj)


db.add_url_rule("/", view_func=DashboardDefault.as_view('index'))
db.add_url_rule("/chart/<chart_id>", view_func=DashboardChart.as_view('chart'))
