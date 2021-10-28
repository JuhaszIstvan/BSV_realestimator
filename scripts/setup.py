def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
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
    except Error as e:
        print(e)

def get_scalar_result(conn, sql):
    cursor=conn.cursor()
    cursor.execute(sql)
    return cursor.fetchone()[0]

def run_command(conn,sqlstring):
    cur = conn.cursor()
    cur.execute(sqlstring)
    rows = cur.fetchall()
    for row in rows:
        print(row)    

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
sql_drop_hirdetesek = """DROP TABLE hirdetesek;"""

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
WHERE NOT EXISTS (SELECT ID FROM hirdetesek WHERE hirdetesek.ID = TEMP.ID and TEMP.httpcode!=404);  """

if __name__ == '__main__':
    import sqlite3
    from sqlite3 import Error
    import os
    import pandas as pd
    import configparser
    config=configparser.ConfigParser()
    scriptdir=os.path.dirname(os.path.realpath(__file__))
    paramfile=os.path.join(scriptdir,'params.ini')
    config.read(paramfile)
    for environment in ['UAT','PROD']:
        outputfld=config[environment]['outputfld']
        if not os.path.isdir(outputfld):
            print(rf'Creating {environment} output directory at {outputfld}')
            os.makedirs(outputfld)
        else:
            print(rf'The output directory already exists at {outputfld}')
        db_file=os.path.join(outputfld,rf'BSV_{environment}.db')
        print(rf'Creating {environment} sqlite database at {db_file}')
        conn=create_connection(db_file)
        try:
            run_command(conn,"DROP TABLE TEMP;")
        except:
            pass
        create_table(conn,sql_create_temp)
        
        try:
            run_command(conn,"DROP TABLE TEMP;")
        except:
            pass
        create_table(conn,sql_create_hirdetesek)
        print('Completed')