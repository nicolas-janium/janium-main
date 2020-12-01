import uuid
from datetime import datetime

from nameparser import HumanName
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_test import Activity, Contact, base_dict, get_db_url


def create_new_contact(contact_info, campaignid, clientid, wh_id, wh_type):
    data = {**base_dict, **contact_info}
    contactid = str(uuid.uuid4())
    name = HumanName(data['first_name'] + ' ' + data['last_name'])
    return Contact(
        contactid,
        str(campaignid),
        str(clientid), 
        data['id'],
        name.first,
        name.last,
        data['title'],
        data['company'],
        data['location'],
        data['email'],
        data['phone'],
        data['website'],
        data['profile'],
        wh_id,
        wh_type
    )

def create_new_activity(contactid, action_timestamp, action_code, message, open_messageid):
    return Activity(str(contactid), action_timestamp, action_code, message, open_messageid)

def main():
    db_url = get_db_url()
    db_engine = create_engine(db_url, echo=False)
    session = sessionmaker(bind=db_engine)()

    contact_info = {
        'id': '1234',
        'first_name': 'Alex',
        'last_name': 'White',
        'title': 'Whatever',
        'company': 'Whatever',
    }
    campaignid = 'a4fc093e-1551-11eb-9daa-42010a8002ff'
    clientid = '63bf6eca-1d2b-11eb-9daa-42010a8002ff'
    wh_id = str(uuid.uuid4())
    wh_type = 'connection'

    new_contact = create_new_contact(contact_info, campaignid, clientid, wh_id, wh_type)
    new_activity = create_new_activity(new_contact.id, None, 1, None, None)
    # new_activity = create_new_activity('00f0be86-5a98-4323-8a68-9da074bb49a1', None, 1, None, None)
    for x in ['23ea57d4-f0c6-4322-a9be-619c3aadfca5']:
        new_activity = create_new_activity(x, datetime.now(), 3, 'Hello there there there there', None)
        session.add(new_activity)
        session.commit()

    # session.add(new_contact)
    # session.add(new_activity)
    # session.commit()


if __name__ == '__main__':
    main()
