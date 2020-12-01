import base64
import json
from datetime import datetime

from google.cloud import pubsub_v1
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sal_db import Campaign, Client, Client_manager, get_db_url


def get_callback(f, clientid):
    def callback(f):
        try:
            messageid = f.result()
            print("Successfully sent pubsub message to poll-webhook-topic. Messageid: {}. Clientid: {}".format(messageid, clientid))
        except:
            print("Pubsub message failed to send to poll-webhook-topic. Message future exception: {}".format(f.exception()))
    return callback

def main(event, context):
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    payload_json = json.loads(pubsub_message)
    if payload_json and 'from' in payload_json: # pylint: disable=too-many-nested-blocks
        if payload_json['from'] == 'janium-main-scheduler':
            db_url = get_db_url()
            db_engine = create_engine(db_url, echo=False)
            session = sessionmaker(bind=db_engine)()

            active_clients = session.query(Client).filter(Client.isactive == 1).all()

            for client in active_clients:
                ### Poll Webhooks and save ###
                ###                        ###
                try:
                    project_id = "janium0-0"
                    topic_id = "poll-webhook-topic"
                    publisher = pubsub_v1.PublisherClient()
                    topic_path = publisher.topic_path(project_id, topic_id) # pylint: disable=no-member
                    pwf_payload = {
                        "trigger-type": "function",
                        "from": "director-function",
                        "data": {
                            "webhooks": [
                                {"url": client.new_connection_wh, "type": "new_connection"},
                                {"url": client.new_message_wh, "type": "new_message"},
                                {"url": client.send_message_wh, "type": "send_message"}
                            ],
                            "clientid": client.id
                        }
                    }

                    future = publisher.publish(topic_path, json.dumps(pwf_payload).encode('utf-8'))
                    future.add_done_callback(get_callback(future, client.id))
                except Exception as err:
                    print("There was an error in publishing a message to the poll-webhook-topic. Error {}".format(err))


                ### Send daily tasks email ###
                ###                        ###
                try:
                    now = datetime.now()
                    deadline = datetime(now.year, now.month, now.day, 16, 00)
                    time_remaining = deadline - now
                    if time_remaining.days == 0 and now.weekday() not in [5,6]:
                        clientmanager = session.query(Client_manager).filter(Client_manager.id == client.clientmanager).first()
                        project_id = "janium0-0"
                        topic_id = "send-daily-tasks-topic"
                        publisher = pubsub_v1.PublisherClient()
                        topic_path = publisher.topic_path(project_id, topic_id) # pylint: disable=no-member

                        sdf_payload = {
                            "trigger-type": "function",
                            "from": "director-function",
                            "data": {
                                "clientid": client.id,
                                "client_firstname": client.firstname,
                                "client_email": client.email,
                                "client_ulincid": client.ulincid,
                                "client_manager_name": clientmanager.name,
                                "campaign_management_email": client.campaign_management_email,
                                "client_manager_lpass_email_id": clientmanager.lpass_email,
                                "daily_tasks_email_id": client.daily_tasks_email_id
                            }
                        }

                        future = publisher.publish(topic_path, json.dumps(sdf_payload).encode('utf-8'))
                        future.add_done_callback(get_callback(future, client.id))
                    else:
                        print("skipping daily tasks email. Now variable: {}. Deadline variable: {}. Time remaining variable: {}".format(now, deadline, time_remaining))
                except Exception as err:
                    print("There was an error in publishing a message to the send-daily-tasks-topic. Error {}".format(err))

                ### Send email to dormant cold contacts ###
                ###                                     ###
                active_campaigns = session.query(Campaign).filter(Campaign.clientid == client.id).filter(Campaign.isactive == 1).all()
                for active_campaign in active_campaigns:
                    if active_campaign.id == '945e974d-2a75-11eb-865a-42010a3d0004':
                        break
                    try:
                        project_id = "janium0-0"
                        topic_id = "send-email-topic"
                        publisher = pubsub_v1.PublisherClient()
                        topic_path = publisher.topic_path(project_id, topic_id) # pylint: disable=no-member

                        with db_engine.connect() as conn:
                            query = "call fetch_email_targets('{}', '{}', '{}');".format(client.id, active_campaign.id, active_campaign.janium_campaign_id)
                            email_targets = conn.execute(query)

                        email_targets_list = []
                        for email_target in email_targets:
                            email_target_dict = {
                                "contactid": email_target[0],
                                "contact_firstname": email_target[1],
                                "contact_email": email_target[2],
                                "email_subject": email_target[3],
                                "email_body": email_target[4],
                                "client_fullname": email_target[5],
                                "client_smtp_address": email_target[6],
                                "lpass_email": email_target[7]
                            }
                            email_targets_list.append(email_target_dict)

                        if len(email_targets_list) == 0:
                            break

                        sef_payload = {
                            "trigger-type": "function",
                            "from": "director-function",
                            "data": email_targets_list
                        }

                        future = publisher.publish(topic_path, json.dumps(sef_payload).encode('utf-8'))
                        future.add_done_callback(get_callback(future, client.id))

                    except Exception as err:
                        print("There was an error in publishing a message to the send-email-topic. Error: {}".format(err))
        else:
            print("The pubsub message was not sent from the janium-main-scheduler job")
    else:
        print("Pubsub message payload is the 'from' key")
