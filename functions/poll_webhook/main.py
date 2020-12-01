import base64
import json
import uuid
from datetime import datetime, timedelta

import demoji
import requests
from google.cloud import pubsub_v1
from nameparser import HumanName
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import sal_db
from sal_db import (Activity, Campaign, Client, Contact, New_connection_wh_res,
                New_message_wh_res, Send_message_wh_res, get_db_url)


def scrub_name(name):
    return HumanName(demoji.replace(name.replace(',', ''), ''))

def create_new_contact(contact_info, campaignid, clientid, wh_id, wh_type):
    data = {**db.base_dict, **contact_info}
    contactid = str(uuid.uuid4())
    name = scrub_name(data['first_name'] + ' ' + data['last_name'])
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

def save_webhook_res(clientid, res, res_type, session):
    resid = str(uuid.uuid4())
    if res_type == 'new_connection':
        inst = New_connection_wh_res(resid, clientid, res)
    elif res_type == 'new_message':
        inst = New_message_wh_res(resid, clientid, res)
    elif res_type == 'send_message':
        inst = Send_message_wh_res(resid, clientid, res)
    session.add(inst)
    session.commit()
    # print('{} webhook response saved successfully. Id: {}'.format(res_type, resid))
    return resid

def poll_webhook(wh_url):
    try:
        return requests.get(wh_url).json()
    except Exception as err:
        print('Error in polling this webhook url: {} \nError: {}'.format(wh_url, err))

def handle_jdata(client, wh_res_id_dict, session):
    wh_type = wh_res_id_dict['type']
    wh_id = wh_res_id_dict['id']

    if wh_type == 'new_connection':
        wh_res = session.query(New_connection_wh_res).filter(New_connection_wh_res.id == wh_id).first().jdata
        for item in wh_res:
            if query := session.query(Campaign).filter(Campaign.clientid == client.id).filter(Campaign.ulincid == str(item['campaign_id'])).first():
                campaignid = query.id
            else:
                # print('Inserting the contact with the Unknown campaignid\nDetails of new_connection item: {}'.format(item))
                campaignid = 'a4fc093e-1551-11eb-9daa-42010a8002ff'

            new_contact = create_new_contact(item, campaignid, client.id, wh_id, wh_type)
            session.add(new_contact)

            new_activity = create_new_activity(new_contact.id, None, 1, None, None)
            session.add(new_activity)
    elif wh_type in ('new_message', 'send_message'):
        if wh_type == 'new_message':
            wh_res = session.query(New_message_wh_res).filter(New_message_wh_res.id == wh_id).first().jdata
        else:
            wh_res = session.query(Send_message_wh_res).filter(Send_message_wh_res.id == wh_id).first().jdata
        for item in wh_res:
            if contact := session.query(Contact).filter(Contact.ulincid == str(item['id'])).first(): # if contact exists in the contact table
                contactid = contact.id
            else:
                if query := session.query(Campaign).filter(Campaign.clientid == client.id).filter(Campaign.ulincid == str(item['campaign_id'])).first():
                    campaignid = query.id
                else:
                    # print('Inserting the contact with the Unknown campaignid\nDetails of {} item: {}'.format(wh_type, item))
                    campaignid = 'a4fc093e-1551-11eb-9daa-42010a8002ff' # unkown campaignid

                new_contact = create_new_contact(item, campaignid, client.id, wh_id, wh_type)
                contactid = new_contact.id
                session.add(new_contact)

            new_activity = create_new_activity(contactid, datetime.strptime(item['time'], "%B %d, %Y, %I:%M %p") - timedelta(hours=2), 2 if wh_type == 'new_message' else 3, item['message'], None)
            session.add(new_activity)
    else:
        print('Webhook type ({}) not recognized'.format(wh_type))
        return

    session.commit()

def main(event, context):
    demoji.download_codes()
    db_url = get_db_url()
    db_engine = create_engine(db_url, echo=False)
    session = sessionmaker(bind=db_engine)()

    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    payload_json = json.loads(pubsub_message)

    if payload_json and 'from' in payload_json and 'data' in payload_json:
        if payload_json['from'] == 'director-function':
            webhooks = payload_json['data']['webhooks']
            client = session.query(Client).filter(Client.id == payload_json['data']['clientid']).first()

            wh_res_id_list = []
            for wh in webhooks:
                wh_res = poll_webhook(wh['url'])
                if len(wh_res) > 0:
                    wh_res_id = save_webhook_res(client.id, wh_res, wh['type'], session) #  Save the webhook response into the mysql instance
                    wh_res_id_list.append(
                        {
                            'type': wh['type'],
                            'id': wh_res_id
                        }
                    )
                else:
                    print('{} webhook response was empty for client {} {}'.format(wh['type'], client.firstname, client.lastname))
            if len(wh_res_id_list) > 0:
                for item_dict in wh_res_id_list:
                    handle_jdata(client, item_dict, session) #  Handle the jdata from the webhook response by parsing and inserting into the contacts and activity tables
            print('Saved and handled all webhook responses')
        else:
            print("The pubsub message was not sent from the director-function function")
    else:
        print("Pubsub message payload is missing the from, webhooks, or clientid keys")
