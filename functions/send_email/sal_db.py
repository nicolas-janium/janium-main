from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import FetchedValue
from sqlalchemy import engine
import os


Base = declarative_base()

class Client(Base):
    __tablename__ = 'client'

    id = Column(String(36), primary_key=True, nullable=False)
    dateadded = Column(DateTime, server_default=FetchedValue())
    firstname = Column(String(250), nullable=False)
    lastname = Column(String(250), nullable=False)
    title = Column(String(250))
    company = Column(String(250))
    location = Column(String(250))
    email = Column(String(250))
    campaign_management_email = Column(String(250))
    phone = Column(String(250))
    ulincid = Column(String(36), nullable=False)
    lpass_email = Column(String(250))
    lpass_ulinc = Column(String(250))
    lpass_li = Column(String(250))
    email_server_id = Column(Integer, nullable=False)
    new_connection_wh = Column(String(250))
    new_message_wh = Column(String(250))
    send_message_wh = Column(String(250))
    isactive = Column(Boolean, nullable=False)
    clientmanager = Column(String(36), nullable=False)
    daily_tasks_email_id = Column(String(36))
    client_sheet_id = Column(String(100))
    ulinc_cookie_id = Column(String(100))
    dateupdated = Column(DateTime, server_default=FetchedValue())


class Campaign(Base):
    __tablename__ = 'campaign'

    id = Column(String(36), primary_key=True, nullable=False)
    dateadded = Column(DateTime, server_default=FetchedValue())
    clientid = Column(String(36), nullable=False)
    ulincid = Column(String(20), nullable=False)
    janium_campaign_id = Column(String(36), nullable=False)
    name = Column(String(250))
    email_after_c_body = Column(Text)
    email_after_c_subject = Column(String(500))
    email_after_c_delay = Column(Integer)
    email_after_wm_body = Column(Text)
    email_after_wm_subject = Column(String(500))
    email_after_wm_delay = Column(Integer)
    dateupdated = Column(DateTime, server_default=FetchedValue())
    isactive = Column(Boolean, nullable=False)


class Contact(Base):
    __tablename__ = 'contact'

    def __init__(self, contactid, campaign_id, clientid, ulincid, firstname, lastname, title,
                 company, location, email, phone, website, li_profile_url, from_wh_id, from_wh_type
                ):
        self.id = contactid
        self.campaignid = campaign_id
        self.clientid = clientid
        self.ulincid = ulincid
        self.firstname = firstname
        self.lastname = lastname
        self.title = title
        self.company = company
        self.location = location
        self.email = email
        self.phone = phone
        self.website = website
        self.li_profile_url = li_profile_url
        self.from_wh_id = from_wh_id
        self.from_wh_type = from_wh_type

    id = Column(String(36), primary_key=True, nullable=False)
    campaignid = Column(String(36), nullable=False)
    clientid = Column(String(36), nullable=False)
    ulincid = Column(String(20), nullable=False)
    dateadded = Column(DateTime, server_default=FetchedValue())
    firstname = Column(String(250), nullable=False)
    lastname = Column(String(250), nullable=False)
    title = Column(String(250))
    company = Column(String(250))
    location = Column(String(250))
    email = Column(String(250))
    phone = Column(String(250))
    website = Column(String(250))
    li_profile_url = Column(String(500))
    dateupdated = Column(DateTime, server_default=FetchedValue())
    from_wh_id = Column(String(36), nullable=False)
    from_wh_type = Column(String(36), nullable=False)


class Activity(Base):
    __tablename__ = 'activity'

    def __init__(self, contactid, action_timestamp, action_code, action_message, open_messageid):
        self.contactid = contactid
        self.action_timestamp = action_timestamp
        self.action_code = action_code
        self.action_message = action_message
        self.open_messageid = open_messageid

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    contactid = Column(String(36), nullable=False)
    dateadded = Column(DateTime, server_default=FetchedValue())
    action_timestamp = Column(DateTime)
    action_code = Column(Integer, nullable=False)
    action_message = Column(Text)
    open_messageid = Column(String(36))

class Action(Base):
    __tablename__ = 'action'

    def __init__(self, action_code, action_name):
        self.action_code = action_code
        self.action_name = action_name

    action_code = Column(Integer, nullable=False, primary_key=True)
    action_name = Column(String(250), nullable=False)


class New_connection_wh_res(Base):
    __tablename__ = 'new_connection_wh_res'

    def __init__(self, id, clientid, jdata):
        self.id = id
        self.clientid = clientid
        self.jdata = jdata
    
    id = Column(String(36), primary_key=True)
    clientid = Column(String(36), nullable=False)
    dateadded = Column(DateTime, server_default=FetchedValue())
    jdata = Column(JSON, nullable=False)

class New_message_wh_res(Base):
    __tablename__ = 'new_message_wh_res'

    def __init__(self, id, clientid, jdata):
        self.id = id
        self.clientid = clientid
        self.jdata = jdata
    
    id = Column(String(36), primary_key=True)
    clientid = Column(String(36), nullable=False)
    dateadded = Column(DateTime, server_default=FetchedValue())
    jdata = Column(JSON, nullable=False)

class Send_message_wh_res(Base):
    __tablename__ = 'send_message_wh_res'

    def __init__(self, id, clientid, jdata):
        self.id = id
        self.clientid = clientid
        self.jdata = jdata

    id = Column(String(36), primary_key=True)
    clientid = Column(String(36), nullable=False)
    dateadded = Column(DateTime, server_default=FetchedValue())
    jdata = Column(JSON, nullable=False)

class Client_manager(Base):
    __tablename__ = 'client_manager'

    id = Column(String(36), nullable=False, primary_key=True)
    name = Column(String(100), nullable=False)
    lpass_email = Column(String(20), nullable=False)
    email = Column(String(100))

class Daily_tasks_email(Base):
    __tablename__ = 'daily_tasks_email'

    id = Column(String(36), nullable=False, primary_key=True)
    name = Column(String(250), nullable=False)
    clientmanagerid = Column(String(36), nullable=False)
    subject = Column(String(1000), nullable= False)
    body = Column(Text, nullable= False)

class Email_server(Base):
    __tablename__ = 'email_server'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    smtp_address = Column(String(100), nullable=False)
    smtp_tls_port = Column(Integer, nullable=False)
    smtp_ssl_port = Column(Integer, nullable=False)

class Ulinc_cookie(Base):
    __tablename__ = 'ulinc_cookie'

    id = Column(Integer, primary_key=True)
    dateadded = Column(DateTime, server_default=FetchedValue())
    clientid = Column(String(36), nullable=False)
    usr = Column(String(100), nullable=False)
    pwd = Column(Integer, nullable=False)
    expires = Column(DateTime, nullable=False)

base_dict = dict({
        'campaign_id': 0,
        'id': None,
        'first_name': None,
        'last_name': None,
        'title': None,
        'company': None,
        'location': None,
        'email': None,
        'phone': None,
        'website': None,
        'profile': None
    })

def get_db_url():
    if os.getenv('IS_CLOUD') == 'True':
        host = os.getenv('DB_HOST')
        port = os.getenv('DB_PORT')
        driver_name = os.getenv('DRIVER_NAME')
        db_name = os.getenv('DB_NAME')
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')
        return engine.url.URL(
            drivername=driver_name,
            username=db_user,
            password=db_password,
            database=db_name,
            host=host,
            port=int(port)
        )

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
# Hey