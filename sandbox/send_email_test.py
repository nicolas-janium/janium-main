import base64
import json
import os
import random
import smtplib
import string
from datetime import datetime
from email.header import Header
from email.message import EmailMessage
from email.utils import make_msgid

import google.auth
import lastpass
from bs4 import BeautifulSoup as Soup
from google.cloud import secretmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sal_db_test import Activity, get_db_url

if os.getenv('IS_CLOUD') == 'True':
    pass
else:
    from dotenv import load_dotenv
    load_dotenv()


def message_id_generator():
    rstring = ''.join(random.choice(string.ascii_letters) for x in range(13))
    return make_msgid(domain='mail.gmail.com', idstring=rstring)

def get_lpass_master():
    creds, project = google.auth.default()
    client = secretmanager.SecretManagerServiceClient(credentials=creds)
    secret_name = "janium-lastpass-masterpass"
    project_id = "janium0-0"
    request = {"name": f"projects/{project_id}/secrets/{secret_name}/versions/latest"}
    response = client.access_secret_version(request)
    return response.payload.data.decode('UTF-8')

def get_credentials(lpass_id):
    vault = lastpass.Vault.open_remote('nic@janium.io', get_lpass_master())
    return [(i.username.decode('UTF-8'), i.password.decode('UTF-8')) for i in vault.accounts if i.id == bytes(lpass_id, 'utf-8')][0]

def add_tracker(email_html, contactid, messageid):
    tracker_url = str(os.getenv('TRACKER_URL'))
    tracker_url += "?contactid={}&messageid={}".format(contactid, messageid)
    soup = Soup(email_html, 'html.parser')
    div = soup.new_tag('div')
    img = soup.new_tag('img', attrs={'height': '0', 'width': '0', 'src': tracker_url})
    div.append(img)
    soup.append(div)
    return str(soup)


def send_email(details, session):
    username, password = get_credentials(details['lpass_email'])
    if details['client_fullname'] == 'Nicolas Arnold':
        recipient = 'nic@janium.io'
    else:
        recipient = details['contact_email']

    contactid = details['contactid']
    messageid = message_id_generator()
    main_email = EmailMessage()

    main_email['Subject'] = details['email_subject']
    main_email['From'] = str(Header('{} <{}>')).format(details['client_fullname'], username)
    main_email['To'] = recipient
    main_email['Message-ID'] = messageid

    email_html = add_tracker(details['email_body'], contactid, messageid)
    email_html = email_html.replace(r"{FirstName}", details['contact_firstname'])
    main_email.set_content(email_html, 'html')

    try:
        with smtplib.SMTP(details['client_smtp_address'], 587) as server:
            server.ehlo()
            server.starttls()
            server.login(username, password)
            server.send_message(main_email)
            print("sent email to {}".format(recipient))

        activity = Activity(contactid, datetime.now(), 4, email_html, messageid)
        session.add(activity)
        session.commit()

    except Exception as err:
        print(err)

def main(event, context):
    db_url = get_db_url()
    db_engine = create_engine(db_url, echo=False)
    session = sessionmaker(bind=db_engine)()

    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    payload_json = json.loads(pubsub_message)

    if payload_json and 'from' in payload_json and 'data' in payload_json:
        if payload_json['from'] == 'director-function':
            for item in payload_json['data']:
                send_email(item, session)
        else:
            print("The pubsub message was not sent from the director-function function")
    else:
        print("Pubsub message payload is missing the from or data keys")

# if __name__ == '__main__':
#     db_url1 = get_db_url()
#     db_engine1 = create_engine(db_url1, echo=False)
#     session1 = sessionmaker(bind=db_engine1)()

#     sef_payload = {
#     "trigger-type": "function",
#     "from": "director-function",
#     "data": [
#         {
#             "contactid": "9ae1be71-38e9-4cbd-a21a-2bf2321d31ca",
#             "contact_firstname": "Bryce",
#             "contact_email": "narnold113@gmail.com",
#             "email_subject": "This is a wm subject line",
#             "email_body": session1.query(Campaign).filter(Campaign.id == 'da13185f-1d68-11eb-9daa-42010a8002ff').first().email_after_wm_body,
#             "client_fullname": "Nicolas Arnold",
#             "client_smtp_address": "smtp.gmail.com",
#             "lpass_email": "5028567445048557853"
#         }
#         ]
#     }
#     sef_payload = json.dumps(sef_payload)
#     # print(sef_payload)

#     sef_payload = base64.b64encode(str(sef_payload).encode("utf-8"))

#     event = {
#         "data": sef_payload
#     }

#     main(event, 1)