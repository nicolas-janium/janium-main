import google.auth
import gspread
import pandas as pd
from google.oauth2 import service_account
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_test import (Campaign, Client, Client_manager, Daily_tasks_email,
                     get_db_url)


def get_sh_session():
    scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
    credentials = service_account.Credentials.from_service_account_file('/home/nicolas/gcp/key.json', scopes=scope)
    return  gspread.authorize(credentials)

def create_client_sheet(clientid, sql_session, sh_session):
    client = sql_session.query(Client).filter(Client.id == clientid).first()
    client_manager = sql_session.query(Client_manager).filter(Client_manager.id == client.client_manager_id).first()
    try:
        new_sh = sh_session.create('Janium Client Sheet - {} {}'.format(client.firstname, client.lastname))
        new_sh_id = new_sh.id()
        new_sh.share(client_manager.email, perm_type='user', role='reader') ## Client manager
        new_sh.share(client.email, perm_type='user', role='reader') ## Client
    except Exception as err:
        print("Failed to create new Client Sheet for {}.\nError: {}".format(client.id, err))

def create_dataset(clientid, db_engine):
    
    contacts = pd.read_sql_query("CALL fetch_contacts('{}')".format(clientid), db_engine)

    print(contacts)


def main():
    db_url = get_db_url()
    db_engine = create_engine(db_url, echo=False)
    sql_session = sessionmaker(bind=db_engine)()

    scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
    credentials = service_account.Credentials.from_service_account_file('/home/nicolas/gcp/key.json', scopes=scope)
    sh_session = gspread.authorize(credentials)

    client = 
    jason_id = 'e98f3c45-2f62-11eb-865a-42010a3d0004'
    nic_id = '63bf6eca-1d2b-11eb-9daa-42010a8002ff'

    # try:
    #     sh = sh_session.open_by_key('1DylxuseYORVaSBxdHLsJK9WEuxJPa_l7dIy2Kv5nkI0')
    #     print('Opened spreadsheet')
    # except gspread.exceptions.SpreadsheetNotFound as err:
    #     print('Spreadsheet not found. Creating one for client.')
    #     create_client_sheet(jason_id, sql_session, sh_session)

    create_dataset(jason_id, db_engine)
if __name__ == '__main__':
    main()
