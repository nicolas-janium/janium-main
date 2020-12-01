from sal_db import Activity, get_db_url
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

def main(request):
    args = request.args

    db_url = get_db_url()
    db_engine = create_engine(db_url, echo=False)
    session = sessionmaker(bind=db_engine)()

    existing_opens = session.query(Activity).filter(Activity.open_messageid == args['messageid']).all()

    if len(existing_opens) > 0:
        return 'The open has already been recorded. Skipping insert query'

    activity = Activity(args['contactid'], datetime.now(), 5, None, args['messageid'])
    session.add(activity)
    session.commit()
    print('Email opened and tracked')
    return ''