import os
from db_test import Client, Campaign, Contact, Activity, get_db_url
from sqlalchemy import create_engine, engine
from sqlalchemy.orm import sessionmaker
import requests
from pprint import pprint


def main(event, context):
    db_url = get_db_url()
    db_engine = create_engine(db_url, echo=False)
    session = sessionmaker(bind=db_engine)()

    active_clients = session.query(Client).filter(Client.isactive == 1).all()

    for client in active_clients:
        # webhooks = [
        #     {'url': client.new_connection_wh, 'type': 'new_connection'},
        #     {'url': client.new_message_wh, 'type': 'new_message'},
        #     {'url': client.send_message_wh, 'type': 'send_message'}
        # ]
        # payload = {
        #     'webhooks': webhooks,
        #     'clientid': client.id
        # }
        # poll_webhooks_res = requests.post(url=os.getenv('POLL_WEBHOOK_FUNCTION_URL'), json=payload)
        # return poll_webhooks_res.text

        active_campaigns = session.query(Campaign).filter(Campaign.clientid == client.id).filter(Campaign.isactive == 1).all()

        for campaign in active_campaigns:
            print(campaign.name)

            email1_targets_query = """\
            select a.action_timestamp,
                c.id as contactid,
                c.firstname,
                c.email as contactEmail,

                ca.id as campaignid,
                ca.name as campaignName,
                ca.email1_body,
                ca.email1_subject,

                cl.id as clientid,
                concat(cl.firstname, ' ', cl.lastname) as clientFullname,
                cl.email as clientEmail,
                cl.lpass_email
            from (
                select *,
                    row_number() over (partition by contactid order by action_timestamp desc) as rownum
                from activity
            ) a
            inner join contact c on c.id = a.contactid
            inner join campaign ca on ca.id = c.campaignid
            inner join client cl on cl.id = ca.clientid
            where a.action_timestamp > ca.dateadded
            and c.email is not NULL
            and a.rownum = 1
            and a.action_code = 3
            and datediff(now(), a.action_timestamp) >= 2
            and ca.id = '{}'
            order by a.action_timestamp desc
            limit 50;
            """.format(campaign.id)

            with db_engine.connect() as conn:
                rs = conn.execute(email1_targets_query)

            email_targets_list = []
            for row in rs:
                email_target = {
                    'contact_firstname': row.firstname,
                    'contactid': row.contactid,
                    'contact_email': row.contactEmail,
                    'client_fullname': row.clientFullname,
                    'lpass_email': row.lpass_email,
                    'email1_subject': row.email1_subject,
                    'email1_body': row.email1_body
                }
                email_targets_list.append(email_target)
            
            print("Sending email1 targets list")
            pprint(email_targets_list)

if __name__ == '__main__':
    main(1, 2)