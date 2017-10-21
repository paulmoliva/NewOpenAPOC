from . import base_model

from database import db


class Contribution(db.Model, base_model.BaseModel):
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
