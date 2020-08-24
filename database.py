import sqlite3

from bs4 import BeautifulSoup
from utils import *
from scrape import *

DB_LOCATION = sqlite3.connect('bills.db')

sql_create_bill_links_table = """ CREATE TABLE bill_links (
                                       id integer PRIMARY KEY,
                                       bill_search_link text,
                                       bill_search_link1 text,
                                       bill_pdf_link text
                                   ); """


c = DB_LOCATION.cursor()


sql_create_subscribers_table = """ CREATE TABLE subscribers (
                                        email text primary key 
);"""

c.execute("DROP TABLE subscribers")
c.execute(sql_create_subscribers_table)


DB_LOCATION.commit()
