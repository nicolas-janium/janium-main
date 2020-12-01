import base64
import json
import smtplib
from email.header import Header
from email.message import EmailMessage

import google.auth
import lastpass
from bs4 import BeautifulSoup as Soup
from google.cloud import secretmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sal_db import Daily_tasks_email, get_db_url


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

def populate_table(email_body, data_set_dict):
    soup = Soup(email_body, 'html.parser')
    if data_set_dict['type'] == 'connection':
        tbody = soup.find("div", id="new-connections").tbody
    elif data_set_dict['type'] == 'message':
        tbody = soup.find("div", id="new-messages").tbody
    for i, row in enumerate(data_set_dict['data']):
        tr_tag = soup.new_tag("tr", **{'class': 'table-row'})
        for j, item in enumerate(row):
            if j == 5:
                break
            if i % 2 == 0:
                if j == 0:
                    td = soup.new_tag("td", **{'class': 'tg-kmlv'})
                    name = soup.new_tag("a", href=str(row[5]))
                    name.string = str(item)
                    td.append(name)
                    tr_tag.append(td)
                else:
                    td = soup.new_tag("td", **{'class': 'tg-kmlv'})
                    td.string = str(item)
                    tr_tag.append(td)
            else:
                if j == 0:
                    td = soup.new_tag("td", **{'class': 'tg-vmfx'})
                    name = soup.new_tag("a", href=str(row[5]))
                    name.string = str(item)
                    td.append(name)
                    tr_tag.append(td)
                else:
                    td = soup.new_tag("td", **{'class': 'tg-vmfx'})
                    td.string = str(item)
                    tr_tag.append(td)
        tbody.append(tr_tag)
    return str(soup)

def tailor_email(email_body, client_ulinc_id, client_firstname):
    soup = Soup(email_body, 'html.parser')

    firstname_tag = soup.find("a", id="client-name")
    firstname_tag.string = client_firstname

    ulinc_inbox_tag = soup.find("a", id="ulinc-inbox")
    ulinc_inbox_tag['href'] = "https://ulinc.co/{}/all".format(client_ulinc_id)
    ulinc_dashboard_tag = soup.find("a", id="ulinc-dashboard")
    ulinc_dashboard_tag['href'] = "https://ulinc.co/{}/".format(client_ulinc_id)

    return str(soup)

def send_email(email_body, subject, details):
    username, password = get_credentials(details['client_manager_lpass_email_id'])
    recipients = [details['client_email'], details['campaign_management_email']]
    main_email = EmailMessage()

    main_email['Subject'] = subject
    main_email['From'] = str(Header('{} <{}>')).format(details['client_manager_name'], username)
    main_email['To'] = recipients

    main_email.set_content(email_body, 'html')

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(username, password)
        server.send_message(main_email)
        print('Sent daily tasks emails to {} for client {}'.format(recipients, details['client_firstname']))
    except Exception as err:
        print(err)
    finally:
        server.close()

def main(event, context):
    db_url = get_db_url()
    db_engine = create_engine(db_url, echo=False)
    session = sessionmaker(bind=db_engine)()

    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    payload_json = json.loads(pubsub_message)

    if payload_json and 'from' in payload_json and 'data' in payload_json:
        if payload_json['from'] == 'director-function':
            details = payload_json['data']
            with db_engine.connect() as conn:
                data_sets = [
                    {
                        'type': 'connection',
                        'data': conn.execute("call new_connections('{}');".format(details['clientid']))
                    },
                    {
                        'type': 'message',
                        'data': conn.execute("call new_messages('{}');".format(details['clientid']))
                    }
                ]
            try:
                email_body = session.query(Daily_tasks_email).filter(Daily_tasks_email.id == details['daily_tasks_email_id']).first().body
                email_subject = session.query(Daily_tasks_email).filter(Daily_tasks_email.id == details['daily_tasks_email_id']).first().subject
            except Exception as err:
                print("There was an error while querying the DB for email_body and subject. Error: {}".format(err))

            for data_set in data_sets:
                email_body = populate_table(email_body, data_set)

            email_body = tailor_email(email_body, details['client_ulincid'], details['client_firstname'])
            send_email(email_body, email_subject, details)
        else:
            print("The pubsub message was not sent from the director-function Function")
    else:
        print("Pubsub message payload is missing the from or data key")
