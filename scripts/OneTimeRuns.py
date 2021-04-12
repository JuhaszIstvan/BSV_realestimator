
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

directory=os.path.dirname(os.path.realpath(__file__))
db_file=os.path.join(directory,"ingatlan.db")
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





db_file=r"C:\Users\Letienne\Dropbox\RealEstimator\BSV_DEV.db"
conn=create_connection(db_file)
#create_table(conn,sql_create_hirdetesek)
#get_scalar_result(conn,"SELECT COUNT (*) from TEMP;")
try:
    run_command(conn,"DROP TABLE TEMP;")
except:
    pass

create_table(conn,sql_create_temp)
loadedDF=pd.read_excel(r"C:\Users\Letienne\Dropbox\RealEstimator\2021-02-13.xlsx", index_col=0)  
loadedDF=pd.read_excel(r"C:\Users\Letienne\Dropbox\RealEstimator\output_dev\ingatlan-dot-com_32042529_32042538_2021-02-14-11-53-44.xlsx", index_col=0)  
"C:\Users\Letienne\Dropbox\RealEstimator\output_dev\ingatlan-dot-com_32042529_32042538_2021-02-14-11-53-44.xlsx"

loadedDF.to_sql('TEMP', conn, if_exists='replace')

logging.info(f'Number of entries in hirdetesek {get_scalar_result(conn,"SELECT COUNT (*) from hirdetesek;")}')
print(f'Number of entries in hirdetesek {get_scalar_result(conn,"SELECT COUNT(*) from hirdetesek;")}')
get_scalar_result(conn,"SELECT MAX(ID) from hirdetesek where httpcode!=404;")
run_command(conn,addnewsql)
conn.commit() 
                                                  
get_scalar_result(conn,"SELECT COUNT(*) from hirdetesek;")
get_scalar_result(conn,"SELECT MAX(ID) from hirdetesek;")             
conn.close







if __name__ == '__main__':
    import sqlite3
    from sqlite3 import Error
    import os
    import pandas as pd
    import xlsxwriter
    directory=os.path.dirname(os.path.realpath(__file__))
    db_file=os.path.join(directory,"ingatlan.db")
    conn=create_connection(db_file)
    loadedDF=pd.read_excel(r"C:\Users\Letienne\Dropbox\RealEstimator\output_dev\ingatlan-dot-com_32042529_32042538_2021-02-14-11-53-44.xlsx", index_col=0)  
"C:\Users\Letienne\Dropbox\RealEstimator\output_dev\ingatlan-dot-com_32042529_32042538_2021-02-14-11-53-44.xlsx"
    if conn is not None:
        print("conn exists")
        # create projects table
        #create_table(conn, sql_create_projects_table) 
        #create_table(conn,sql_drop_hirdetesek_table)
        #df = pd.read_sql_query("SELECT * from hirdetesek",conn )
        loadedDF.to_sql('hirdetesek3', conn, if_exists='replace')
        print("loading completed:{}".format(len(loadedDF.index)))
        run_command(conn,"SELECT COUNT (*) from TEMP;")
        #select_all_tasks(conn)
        run_command(conn,"SELECT COUNT (*) from TEMP;")

