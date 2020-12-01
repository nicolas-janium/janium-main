import os
from sal_db_test import Client, Campaign, Contact, Activity, New_connection_wh_res, New_message_wh_res, Send_message_wh_res
from sqlalchemy import create_engine, engine
from sqlalchemy.orm import sessionmaker
import requests
from pprint import pprint
from nameparser import HumanName
import demoji
demoji.download_codes()

def get_db_url():
    if os.getenv('IS_CLOUD'):
        print('In the cloud')
        connection_name = os.getenv('CONNECTION_NAME')
        driver_name = os.getenv('DRIVER_NAME')
        query_string = dict({"unix_socket": "/cloudsql/{}".format(connection_name)})
        db_name = os.getenv('DB_NAME')
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')
        return engine.url.URL(
            drivername=driver_name,
            username=db_user,
            password=db_password,
            database=db_name,
            query=query_string
        )
    else:
        print('Not in the cloud')
        from dotenv import load_dotenv
        load_dotenv()
        host = os.getenv('HOST')
        driver_name = os.getenv('DRIVER_NAME')
        db_name = os.getenv('DB_NAME')
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')
        return engine.url.URL(
            drivername=driver_name,
            username=db_user,
            password=db_password,
            database=db_name,
            host=host
        )

def scrub_name(name):
    return HumanName(demoji.replace(name.replace(',', ''), ''))

def main():
    db_url = get_db_url()
    engine = create_engine(db_url, echo=False)
    session = sessionmaker(bind=engine)()

    wh_id = 'f4e4c0d9-a083-4830-9673-25c431ef56c6'
    ulincid = 56654796531

    # wh_record = session.query(Send_message_wh_res).filter(Send_message_wh_res.id == wh_id).first()
    # wh_record = session.query(New_connection_wh_res).first()
    wh_record = session.query(New_message_wh_res).filter(New_message_wh_res.id == wh_id).first()

    wh_res = wh_record.jdata
    for item in wh_res:
        # pprint(item)
        if item['id'] == ulincid:
            fullname = str(item['first_name'] + ' ' + item['last_name'])
            print(fullname)
            fullname = scrub_name(fullname)
            print(fullname.first)
            break

            # fullname = str(item['first_name'] + ' ' + item['last_name'])
            # name = HumanName(fullname)
            # print(fullname)
            # print(name.first)


if __name__ == '__main__':
    main()