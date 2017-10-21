import flask
import os
import json

from sqlalchemy import and_

from database import db
from models import campaign, contribution, contributor

application = flask.Flask(__name__)

application.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URL') or \
    'mysql+pymysql://cranklogic:cranklogic@127.0.0.1/openapoc'
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
application.secret_key = os.getenv('SECRET_KEY') or 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

db.init_app(application)


@application.errorhandler(404)
def page_not_found(e):
    return flask.render_template('index.html')


@application.route('/')
def index():
    return flask.render_template('index.html')


@application.route('/api/campaigns')
def dump_campaigns():
    all_the_campaigns = campaign.Campaign.query.all()
    result = []
    for each_campaign in all_the_campaigns:
        result.append(each_campaign.as_dict())
    return json.dumps(result)


@application.route('/api/campaigns/<int:campaign_id>/')
def dump_campaign(campaign_id):
    the_contributions = db.session.query(
        contribution.Contribution
    )\
        .filter(
            contribution.Contribution.campaign_id == campaign_id
    )\
        .group_by(
            contribution.Contribution.contributor_id, contribution.Contribution.Report_Year
    )\
        .all()
    result = []
    for each_contribution in the_contributions:
        result.append({
            "id": each_contribution.id,
            "full_name": each_contribution.full_name,
            "total_amount": each_contribution.amount,
            "Report_Year": each_contribution.Report_Year,
            "contributor_id": each_contribution.van_id,
        })
    the_campaign = campaign.Campaign.query.get(campaign_id).as_dict()
    return json.dumps({'contributions': result, 'info': the_campaign})


@application.route('/api/contributors/<int:contributor_id>')
def dump_contributor(contributor_id):
    the_contributions = contribution.Contribution.query.filter(
        contribution.Contribution.contributor_id == contributor_id
    ).all()
    result = []
    for each_contribution in the_contributions:
        result.append(each_contribution.as_dict())
    the_contributor = contributor.Contributor.query.get(
        contributor_id
    ).as_dict()
    return json.dumps({'contributions': result, 'contributor': the_contributor})


@application.route('/api/contributors/search')
def search_contributors():
    search_term = flask.request.args.get('search')
    return contributor.Contributor.find_by_name(search_term)
