import logging 
sql_create_hirdetesek = """ CREATE TABLE IF NOT EXISTS hirdetesek (
                                    ID integer PRIMARY KEY NOT NULL,
                                    hirdetesurl text NOT NULL,
                                    httpcode integer,
                                    address text,
                                    alapterulet integer,
                                    kerulet text,
                                    leiras text,
                                    alkategoria text,
                                    hirdeto text,
                                    iroda text,
                                    ar text,
                                    First_recorded text,
                                    belmagassag text,
                                    price real,
                                    Forward integer,
                                    end_date text,
                                    officeid integer, 
                                    UNIQUE(ID)
                                ); """


sql_create_temp = """ CREATE TABLE IF NOT EXISTS TEMP (
                                    ID integer PRIMARY KEY NOT NULL,
                                    hirdetesurl text NOT NULL,
                                    httpcode integer,
                                    address text,
                                    alapterulet integer,
                                    kerulet text,
                                    leiras text,
                                    alkategoria text,
                                    hirdeto text,
                                    iroda text,
                                    ar text,
                                    First_recorded text,
                                    belmagassag text,
                                    price real,
                                    Forward integer,
                                    end_date text,
                                    officeid integer, 
                                    UNIQUE(ID)
                                ); """

sql_drop_TEMP = """DROP TABLE TEMP;"""

addnewsql=""" INSERT INTO hirdetesek (
ID,
hirdetesurl,
httpcode,
address,
alapterulet,
kerulet,
leiras,
alkategoria,
hirdeto,
iroda,
ar,
First_recorded,
belmagassag,
price,
Forward,
end_date,
officeid) 
SELECT 
    ID,
    hirdetesurl,
    httpcode,
    address,
    alapterulet,
    kerulet,
    leiras,
    alkategoria,
    hirdeto,
    iroda,
    ar,
    First_recorded,
    belmagassag,
    price,
    Forward,
    end_date,
    officeid 
from TEMP
WHERE NOT EXISTS (SELECT ID FROM hirdetesek WHERE hirdetesek.ID = TEMP.ID) and TEMP.httpcode!=404;  """

def create_connection(db_file):
    import sqlite3
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Exception as e:
        print(e)

    return conn

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Exception as e:
        print(e)

def run_command(conn,sqlstring):
    cur = conn.cursor()
    cur.execute(sqlstring)
    rows = cur.fetchall()
    for row in rows:
        print(row)  

def get_scalar_result(conn, sql):
    cursor=conn.cursor()
    cursor.execute(sql)
    return cursor.fetchone()[0]

def sendemail(sender_address,sender_pass,receiver_address,bcc_address,subject,mail_content,excelattachment):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email import encoders
    import os
    #Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = subject   #The subject line
    #The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'plain'))
    fa = open(excelattachment, 'rb')
    part = MIMEBase('application','vnd.ms-excel')
    part.set_payload(fa.read())
    fa.close()
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="'+ os.path.basename(excelattachment)+'"')
    message.attach(part)
    #Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
    session.starttls() #enable security
    session.login(sender_address, sender_pass) #login with mail_id and password
    text = message.as_string()
    session.sendmail(sender_address,receiver_address.split(",")+bcc_address.split(","), text)
    session.quit()
    print('Mail Sent')

def ClearBatch(rsl):
    import pandas as pd
    rsl['millio'] =1
    rsl['arcleared']=rsl.ar.str.replace('.Ft', '', regex=True)
    rsl.loc[rsl['arcleared'].str.contains("millió", na=False), 'millio'] = 1000000
    rsl.loc[rsl['arcleared'].str.contains("milliárd", na=False), 'millio'] = 1000000000
    rsl['arcleared']=rsl.arcleared.str.replace('.millió.*', '', regex=True).str.replace('.milliárd.*', '', regex=True).str.replace(',', '.', regex=True).str.replace('ár nélkül','').str.replace(' ', '', regex=True)
    try:
        rsl.loc[pd.notna(rsl.arcleared), 'price'] = rsl['arcleared'].astype(float)*rsl['millio']
    except:
        rsl.loc[pd.notna(rsl.arcleared), 'price']= None
        logging.error(f"Failed to convert record to float")
    rsl=rsl.drop(['millio','arcleared'], axis=1)
    rsl['Forward'] =False
    rsl.loc[(rsl.httpcode==200) & (pd.isnull(rsl['iroda'])) & (rsl['kerulet'].str.contains('.*kerület|Budapest|Budaörs.*', case=False, regex=True)) & (rsl['alkategoria'].str.contains('.*Eladó.*', case=False, regex=True)) & (rsl['alkategoria'].str.contains('.*Ház|Lakás|üzlet|telek.*', case=False, regex=True))  , 'Forward']=True
    return rsl

def collectads(starter, batchsize):
    from logging import exception 
    from numpy.core.numeric import NaN
    import pandas as pd
    import time, datetime
    import random
    import re
    import numpy as np
    import requests
    from tqdm import tqdm

    resultlist = pd.DataFrame()
    dead=0
    maxdead=25
    baseurl='https://ingatlan.com'
 
    for n in tqdm(range(batchsize)):
        time.sleep(np.exp(random.random())/2)
        hID=starter+n
        hirdetesurl=str(baseurl)+"/"+str(hID)
        logging.debug(hirdetesurl)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0'}
        hData = {"ID": int(hID),
                "hirdetesurl": hirdetesurl,
                'First_recorded':NaN,
                'address':NaN,
                'alapterulet':NaN,
                'kerulet':NaN,                
                'leiras':NaN,
                'belmagassag':NaN,
                'alkategoria':NaN,
                'hirdeto':NaN,
                'iroda':NaN,
                'ar':NaN,
                'officeid':NaN
                }
        try:
            x = requests.get(hirdetesurl, headers=headers)
            logging.debug(x.status_code)
            hData['httpcode'] = x.status_code
            if x.status_code==404:
                dead=dead+1
            else:
                dead=0
            if dead>maxdead:
                logging.info("Too many consecutive broken links. Stopping.")
                break
            if x.status_code==200:
                hWebPageText=x.content.decode()
                hData['First_recorded']=datetime.date.today().strftime("%Y-%m-%d")
                m = re.search('<div class="photo-address">(.*?) </div>', hWebPageText)
                if m is not None:
                    hData['address'] = m.group(1).strip()
                m = re.search('<span class="parameter-value">(.*?)m²</span>', hWebPageText)
                if m is not None:
                    hData['alapterulet'] = int(m.group(1).strip().replace(" ", ""))
                m = re.search('<span itemprop="title">(.*?)</span>', hWebPageText)
                if m is not None:
                    hData['kerulet'] = m.group(1).strip()
                m = re.search('<div class="long-description">(.*?)</div>', hWebPageText)
                hData['leiras']=''
                if m is not None:
                    hData['leiras'] = m.group(1).strip()
                m = re.search('<td>Belmagasság</td> <td>(.*?)</td> </tr>', hWebPageText)        
                if m is not None:
                    hData['belmagassag'] = m.group(1).strip()
                m = re.search('<div class="listing-subtype">(.*?)</div>', hWebPageText)
                if m is not None:
                    hData['alkategoria'] = m.group(1).strip()
                m = re.search('<div class="call-the-advertiser">(.*?)</div>', hWebPageText)         
                if m is not None:
                    hData['hirdeto'] = m.group(1).strip()
                m= None
                m = re.search('<div class="agent-name">(.*?)</div>', hWebPageText)
                if m is not None:
                    hData['iroda'] = m.group(1).strip()
                m= None
                m = re.search('<div class="parameter parameter-price">.*<span class="parameter-value">(.*?)</span>', hWebPageText)
                if m is not None:
                    hData['ar'] = m.group(1).strip()
                m= None
                m = re.search('officeId:(.*?),*.}', hWebPageText)
                if m is not None:
                    hData['officeid'] = m.group(1).strip()
        except:
            logging.error(f'failed to collect: {hData["ID"]}')
        Df=pd.DataFrame([hData])
        Df=Df.set_index('ID')
        if x.status_code==200:
            try:   
                Df=ClearBatch(Df)
            except Exception as e:
                logging.error(e.args)
                print(e)
                logging.error(f"Failed to convert the file {hData['ID']}")
        resultlist = resultlist.append(Df, ignore_index=False)
        if n==batchsize:
            break
    return resultlist

def main(arguments):
    import logging
    import datetime
    import os
    import sqlite3
    from sqlite3 import Error
    environment=''
    batchsize=4000
    try:
        opts, args = getopt.getopt(arguments[1:],"hb:e:s:",["env=","help=","start=","bsize="])
    except getopt.GetoptError:
        print('''error ingatlan_com.py 
                    -e <environment UAT|PROD|DEV>
                    -h for help
                    -b --bsize to set how far should the script count upwards
                    -s to set the first to check''')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(f'''USAGE:
                 ingatlan_com.py 
                    -e <environment UAT|PROD|DEV>
                    -h for help
                    -b --bsize to set how far should the script count. Default is {batchsize}
                    -s to set the first to check''')
            sys.exit()
        elif opt in ("-e", "--env"):
            environment = arg
            if environment not in ['PROD','UAT','DEV']:
                print(f'ingatlan_com.py -e <environment UAT|PROD|DEV> the received value is: {arg}')
                sys.exit(2)
        elif opt in ("-s", "--start"):
            try:
                startat=int(arg)
            except:
                print(f'-s or --start supposed to be numeric! {arg}')
                sys.exit(2)
        elif opt in ("-b", "--bsize"):
            try:
                batchsize=int(arg)
            except:
                print(f'-b or --bsize supposed to be numeric! {arg}')
                sys.exit(2)                
           
    import configparser
    config=configparser.ConfigParser()
    paramfile='/var/opt/realestimator/scripts/params.ini'
    config.read(paramfile)
    print(config.sections())
    sender_address = config[environment]['sender_address']
    sender_pass = config[environment]['sender_pass']
    receiver_address = config[environment]['receiver_address']
    bcc_address = config[environment]['bcc_address']
    subject=f'ingatlan.com szűrési eredmények {datetime.datetime.today().strftime("%Y-%m-%d %H óra")}'

    if environment=='PROD':
        outputfld=os.path.join('/var','opt','realestimator','output_prod')
        logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',filename=os.path.join(outputfld,'ingatlan_com.log'), level=logging.INFO,datefmt='%Y-%m-%d %H:%M:%S')
        db_file=os.path.join(outputfld,'BSV_PROD.db')
   
    elif environment=='UAT':
        outputfld=os.path.join('/var','opt','realestimator','output_dev')
        logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',filename=os.path.join(outputfld,'ingatlan_com_DEV.log'), level=logging.INFO,datefmt='%Y-%m-%d %H:%M:%S')
        db_file=os.path.join(outputfld,'BSV_DEV.db')

    if startat==0:
        conn=create_connection(db_file)
        try:
            startat=get_scalar_result(conn,"SELECT MAX(ID) from hirdetesek where httpcode!=404;") + 1  
            conn.close() 
        except:
            logging.error(f"Failed to retrieve the last valid hirdetes! from the database!")
            sys.exit(2)
    logging.info(f'Starting {environment},{startat}')
    logging.info(f'sender: {sender_address},receiver: {receiver_address}')
    print(f'Starting {environment},{startat}')
    resultlist=collectads(int(startat),batchsize)
    #db upload
    conn=create_connection(db_file)
    nohir=get_scalar_result(conn,"SELECT COUNT (*) from hirdetesek;")
    logging.info(f'Number of entries in hirdetesek {nohir}')
    print(f'Number of entries in hirdetesek {nohir}')
    try:
        run_command(conn,"DROP TABLE TEMP;")
        conn.commit()
        create_table(conn,sql_create_temp)
        conn.commit()
        resultlist.to_sql('TEMP', conn, if_exists='append')
        conn.commit() 
    except:
        logging.error(f'Failed to upload onto the staging DB')
        pass
    try:
        run_command(conn,addnewsql)
        conn.commit() 
        hirafter=get_scalar_result(conn,"SELECT COUNT(*) from hirdetesek;")
        hirmaxafter= get_scalar_result(conn,"SELECT MAX(ID) from hirdetesek where httpcode!=404;")
        conn.close          
    except:
        logging.info(f'failed to execute the DB operations!')
        pass        
    lastHID=resultlist[resultlist.httpcode!=404].index.max()
    filestring=os.path.join(outputfld,"ingatlan-dot-com_" + str(startat)+ '_' + str(lastHID)+ '_' + datetime.datetime.today().strftime("%Y-%m-%d-%H-%M-%S") + '.xlsx')
    resultlist.to_excel(filestring, engine='xlsxwriter',index=True)
    filestring=os.path.join(outputfld,"ingatlan-dot-com_" + datetime.datetime.today().strftime("%Y-%m-%d-%H")  + '_' + str(startat)+ '-' + str(lastHID)+ '.xlsx')
    MIKINEK=resultlist.loc[resultlist.Forward==True]
    MIKINEK.to_excel(filestring, engine='xlsxwriter',index=True)
    mail_content='''
           Szia Miki!,
           Mellékeltem a legfrissebb szűrés eredményét.
           Köszönöm!'''
    sendemail(sender_address,sender_pass,receiver_address,bcc_address,subject,mail_content,filestring)
    print('attachment; filename="'+ os.path.basename(filestring)+'"')
    print(f'Last valid HID found: {lastHID}')
    logging.info(f'Last valid HID found: {lastHID}')
if __name__ == "__main__":
    import sys, getopt
    main(sys.argv)
