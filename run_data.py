from flask_sqlalchemy import SQLAlchemy
import flask, json
import os
from sqlalchemy import or_, and_

application = flask.Flask(__name__)

application.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URL') or \
    'mysql+pymysql://cranklogic:cranklogic@127.0.0.1/openapoc'
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
application.secret_key = os.getenv('SECRET_KEY') or 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

db = SQLAlchemy(application)

SCORE_QUERY = '''
update contributors as t
set t.score = (
	select (sum(contributions.`Amount`) * (case contributions.lean when 'r' then -1 when 'l' then 1 else 0 END))
	from contributions
	where contributions.`contributor_id` = t.`id`
);
'''

ADD_TO_SCORE_QUERY = '''
update contributors as t
set t.add_to_score =
    case t.score < -1
        when true then -1
        else
            case t.score > 1
                when true then 1 else 0
            end
    end
'''

DONORS_LEAN_QUERY ='''
update contributions as t
set lean = (
    select leans from campaigns where campaigns.id = t.campaign_id
);
'''

LEANS_QUERY = '''
update campaigns as t
set leans =
    case ((select sum(con.add_to_score) from contributors con
    join contributions d on d.contributor_id = con.id
    where d.campaign_id = t.id
    ) < -1) when true then 'r' else case((select sum(con.add_to_score) from contributors con
    join contributions d on d.contributor_id = con.id
    where d.campaign_id = t.id
    ) > 1) when true then 'l' else null end end,

score =
    (select sum(con.add_to_score) from contributors con
    join contributions d on d.contributor_id = con.id
    where d.campaign_id = t.id
    );
'''

UPDATE_VOTES_QUERY = '''
update van as t set primary_votes =
    cast(t.`Primary98` as decimal) + cast(t.`Primary00` as decimal) + cast(t.`Primary02` as decimal) + cast(t.`Primary04` as decimal) + cast(t.`Primary06` as decimal) + cast(t.`Primary08` as decimal) + cast(t.`Primary10` as decimal) + cast(t.`Primary12` as decimal) + cast(t.`Primary14` as decimal) + cast(t.`Primary16` as decimal)
)
'''

TRAIN_ORDER = [DONORS_LEAN_QUERY, SCORE_QUERY, ADD_TO_SCORE_QUERY, LEANS_QUERY]


class BaseModel:
    def as_dict(self):
        result = {}
        for attr, value in self.__dict__.items():
            if not value and value != 0:
                result[attr] = None
            else:
                try:
                    result[attr] = int(value)
                except Exception:
                    try:
                        result[attr] = str(value)
                    except Exception:
                        pass
        return result


class Contribution(db.Model, BaseModel):
    __tablename__ = "contributions"
    id = db.Column(db.Integer, primary_key=True)

    contributor_score = db.Column(db.Float)
    contributor_id = db.Column(db.Integer, db.ForeignKey('contributors.id'), index=True, nullable=True)
    amount = db.Column(db.Float)

    Date = db.Column(db.String(255))
    Transaction_Type = db.Column(db.String(255))
    Payment_Type = db.Column(db.String(255))
    Payment_Detail = db.Column(db.String(255))
    Amount = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    first_name = db.Column(db.String(255))
    Address = db.Column(db.String(255))
    City = db.Column(db.String(255))
    State = db.Column(db.String(255))
    zip = db.Column(db.String(255))
    Country = db.Column(db.String(255))
    Occupation = db.Column(db.String(255))
    Employer = db.Column(db.String(255))
    Purpose_of_Expenditure = db.Column(db.String(255))
    Report_Type = db.Column(db.String(255))
    Election_Name = db.Column(db.String(255))
    Election_Type = db.Column(db.String(255))
    Municipality = db.Column(db.String(255))
    Office = db.Column(db.String(255))
    Filer_Type = db.Column(db.String(255))
    Name = db.Column(db.String(255), index=True, nullable=True)
    Report_Year = db.Column(db.String(255))
    Submitted = db.Column(db.String(255))
    lean = db.Column(db.String(1))
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), index=True, nullable=True)
    full_name = db.Column(db.String(255), index=True, nullable=True)

    def __init__(self):
        self.full_name = self.First_Name + ' ' + self.Last_Business_Name
        self.is_person = bool(self.First_Name and len(self.First_Name) > 0)

    def leans(self):
        if self.lean:
            return self.lean
        else:
            return self.campaign.leans


class Campaign(db.Model, BaseModel):
    __tablename__ = 'campaigns'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), index=True)
    election_type = db.Column(db.String(255), index=True)
    office = db.Column(db.String(255), index=True)
    leans = db.Column(db.String(1))
    score = db.Column(db.Float)

    def sum_contributor_score(self):
        print(self.name)
        the_contributor = Contributor.query.filter(Contributor.full_name == (' ' + self.name)).first()
        if the_contributor:
            if the_contributor.get_score() > 500:
                self.leans = 'l'
                db.session.add(self)
                db.session.commit()
                return ''
            elif the_contributor.get_score() < -500:
                self.leans = 'r'
                db.session.add(self)
                db.session.commit()
                return ''
        contributions = self.contributions
        score = 0
        update = False
        seen = {}
        for each_contribution in contributions:
            if each_contribution and each_contribution.contributor and (not seen.get(each_contribution.contributor.full_name)):
                score += each_contribution.contributor.add_to_score
                print(score)
                if (score > 10) or (score < -10):
                    break
        if score > 4:
            self.leans = 'l'
            update = True
        elif score < -4:
            self.leans = 'r'
            update = True
        print(score)
        if update:
            db.session.add(self)
            db.session.commit()


class Contributor(db.Model, BaseModel):
    __tablename__ = 'contributors'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), index=True)
    last_name = db.Column(db.String(255))
    first_name = db.Column(db.String(255))
    zip = db.Column(db.Integer)
    score = db.Column(db.Float)
    add_to_score = db.Column(db.Float)
    avg_score = db.Column(db.Float)
    avg_donation = db.Column(db.Float)
    total = db.Column(db.Float)
    is_person = db.Column(db.Boolean)

    def __init__(self, first_name, last_name, zip):
        self.first_name = first_name
        self.last_name = last_name
        self.full_name = first_name + ' ' + last_name
        self.zip = zip
        self.is_person = bool(len(first_name) > 0)

    def get_score(self):
        if self.score:
            return self.score
        all_contributions = self.contributions
        score = {
            'l': 0,
            'r': 0
        }
        for each_contribution in all_contributions:
            if each_contribution.campaign and each_contribution.campaign.leans:
                score[each_contribution.campaign.leans] += each_contribution.total_amount()
        result = score['l'] - score['r']
        if result != self.score:
            self.score = result
            db.session.add(self)
            db.session.commit()
            print(self.full_name + ' updated to ' + str(self.score))
        return result

    @classmethod
    def find_by_name(cls, search_term, order_by=None, form_submit=None):
        if order_by:
            order_attr = getattr(cls, order_by)
        else:
            order_attr = cls.full_name
        or_statement = or_(
            cls.full_name.ilike('%{0}%'.format(search_term))
        )
        results = cls.query.filter(or_statement).order_by(order_attr).limit(500).all()
        final_array_to_return = [x.as_dict() for x in results]
        if not len(final_array_to_return):
            final_array_to_return.append({
                "id": 0,
                "full_name": "No Results",
                "score": '-1'
            })
        final_array_to_return[0]['formSubmit'] = form_submit
        return json.dumps(final_array_to_return)


def run_test():
    with open('progress.txt', 'r+') as f:
        text = f.read()
        progress_index = int(text)
        while True:
            all_donations = Contribution.query.filter(
                and_(
                    Contribution.id >= progress_index,
                    Contribution.id < (progress_index + 1000)
                )
            ).all()
            if len(all_donations) == 0:
                return ''
            for donation in all_donations:
                print(donation.id)
                the_campaign = Campaign.query.filter(Campaign.name == donation.Name).first()
                if not the_campaign:
                    print('creating ' + donation.Name)
                    new_campaign = Campaign()
                    new_campaign.name = donation.Name
                    new_campaign.election_type = donation.Election_Type
                    new_campaign.office = donation.Office
                    db.session.add(new_campaign)
                    db.session.commit()
                the_contributor = Contributor.query.filter(
                    and_(
                        Contributor.full_name == (donation.first_name + ' ' + donation.last_name),
                        Contributor.zip == donation.zip
                    )
                ).first()
                if not the_contributor:
                    new_contributor = Contributor(donation.first_name, donation.last_name, donation.zip)
                    print('creating ' + donation.first_name + ' ' + donation.last_name)
                    db.session.add(new_contributor)
                    db.session.commit()
                progress_index += 1
            f.seek(0)
            f.write(str(progress_index))
            f.truncate()
            print(progress_index)


def score():
    db.session.execute("SET SESSION sql_mode='TRADITIONAL'")
    for each_query in TRAIN_ORDER:
        db.session.execute(each_query)
    db.session.commit()
score()
