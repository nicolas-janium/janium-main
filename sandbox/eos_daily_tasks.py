import json
import os
import smtplib
from email.header import Header
from email.message import EmailMessage

import google.auth
import lastpass
from bs4 import BeautifulSoup as Soup
from google.cloud import secretmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sal_db_test import Daily_tasks_email, get_db_url


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

def populate_tables(email_body, data_list):
    soup = Soup(email_body, 'html.parser')
    new_cnxn_tbody = soup.find("div", id="new-connections").tbody
    new_msgs_tbody = soup.find("div", id="new-messages").tbody
    for i, data in enumerate(data_list):
        tr_tag = soup.new_tag("tr", **{'class': 'table-row'})

        name_td = soup.new_tag("td", **{'class': 'tg-kmlv' if i%2 == 0 else 'tg-vmfx' })
        li_a_tag = soup.new_tag("a", href=str(data['linkedin_url']))
        li_a_tag.string = str(data['contact_name'])
        name_td.append(li_a_tag)

        title_td = soup.new_tag("td", **{'class': 'tg-kmlv' if i%2 == 0 else 'tg-vmfx' })
        title_td.string = data['title']

        company_td = soup.new_tag("td", **{'class': 'tg-kmlv' if i%2 == 0 else 'tg-vmfx' })
        company_td.string = data['company']

        location_td = soup.new_tag("td", **{'class': 'tg-kmlv' if i%2 == 0 else 'tg-vmfx' })
        location_td.string = data['location']

        campaign_td = soup.new_tag("td", **{'class': 'tg-kmlv' if i%2 == 0 else 'tg-vmfx' })
        campaign_td.string = data['campaign']

        tr_tag.extend([name_td, title_td, company_td, location_td, campaign_td])
        if data['type'] == 'new_connection':
            new_cnxn_tbody.append(tr_tag)
        else:
            new_msgs_tbody.append(tr_tag)
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
    username, password = get_credentials('2575208259370624104')
    recipient = details['client_email']
    main_email = EmailMessage()

    main_email['Subject'] = subject
    main_email['From'] = str(Header('{} <{}>')).format("Mike O'Neil", username)
    main_email['To'] = recipient

    main_email.set_content(email_body, 'html')

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(username, password)
        server.send_message(main_email)
    except Exception as err:
        print(err)
    finally:
        server.close()

def main(event, context):
    db_url = get_db_url()
    db_engine = create_engine(db_url, echo=False)
    session = sessionmaker(bind=db_engine)()

    path = '/home/nicolas/projects/janium/python/tests/eos_tasks_emails'
    obj = os.scandir(path)

    for item in obj:
        if item.is_file():
            f = open(item.path, 'r', encoding='utf-8')
            email_body = session.query(Daily_tasks_email).filter(Daily_tasks_email.id == 'd423ffd9-25e7-11eb-a429-42010a3d0002').first().body
            email_subject = session.query(Daily_tasks_email).filter(Daily_tasks_email.id == 'd423ffd9-25e7-11eb-a429-42010a3d0002').first().subject
            details = json.load(f)
            details['data'] = sorted(details['data'], key=lambda x : x['contact_name'], reverse=False)
            email_body = populate_tables(email_body, details['data'])

            email_body = tailor_email(email_body, details['client_ulincid'], details['client_firstname'])
            # print(email_body)
            send_email(email_body, email_subject, details)


    # f = open('tests/eos_tasks_emails/beth_harmon.json', 'r', encoding='utf-8')
    # details_dict = json.load(f)
    # data_list = details_dict['data']

    # from itertools import groupby
    # from operator import itemgetter

    # for key, value in groupby(data_list):
    #     # for x in key:
    #     #     print(x)
    #     print(key, value)


if __name__ == '__main__':
    main(1,1)