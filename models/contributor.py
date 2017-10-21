import json
from sqlalchemy import or_

from database import db
from . import base_model


class Contributor(db.Model, base_model.BaseModel):
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
    def find_by_name(cls, search_term):
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
        return json.dumps(final_array_to_return)
