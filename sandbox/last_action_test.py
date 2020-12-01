import os
from db_test import Client, Campaign, Contact, Activity, New_connection_wh_res, New_message_wh_res, Send_message_wh_res
from sqlalchemy import create_engine, engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

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

def main():
    db_url = get_db_url()
    engine = create_engine(db_url, echo=False)
    # session = sessionmaker(bind=engine)()

    statement = text(
        """
        select c.id,
            c.firstname,
            c.lastname,
            c.email as contactEmail,

            ca.id as campaignid,
            ca.name as campaignName,
            ca.email1_body,

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
        and datediff(now(), a.action_timestamp) >= 0
        order by c.firstname;
        """
    )

    with engine.connect() as conn:
        rs = conn.execute(statement)

    for i, item in enumerate(rs):
        # print(i + 1)
        print(item)


    
if __name__ == '__main__':
    main()
