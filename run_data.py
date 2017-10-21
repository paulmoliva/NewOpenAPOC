from sqlalchemy import and_

from database import db
from models import campaign, contribution, contributor

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


def run_test():
    with open('progress.txt', 'r+') as f:
        text = f.read()
        progress_index = int(text)
        while True:
            all_donations = contribution.Contribution.query.filter(
                and_(
                    contribution.Contribution.id >= progress_index,
                    contribution.Contribution.id < (progress_index + 1000)
                )
            ).all()
            if len(all_donations) == 0:
                return ''
            for donation in all_donations:
                print(donation.id)
                the_campaign = campaign.Campaign.query.filter(campaign.Campaign.name == donation.Name).first()
                if not the_campaign:
                    print('creating ' + donation.Name)
                    new_campaign = campaign.Campaign()
                    new_campaign.name = donation.Name
                    new_campaign.election_type = donation.Election_Type
                    new_campaign.office = donation.Office
                    db.session.add(new_campaign)
                    db.session.commit()
                the_contributor = contributor.Contributor.query.filter(
                    and_(
                        contributor.Contributor.full_name == (donation.first_name + ' ' + donation.last_name),
                        contributor.Contributor.zip == donation.zip
                    )
                ).first()
                if not the_contributor:
                    new_contributor = contributor.Contributor(donation.first_name, donation.last_name, donation.zip)
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
