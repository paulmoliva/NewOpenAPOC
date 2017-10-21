from . import base_model

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
