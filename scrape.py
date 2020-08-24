# Kwesi Afrifa, Jun-Jul 2020, kwesi@mit.edu
from bs4 import BeautifulSoup
from datetime import datetime

import re
import requests
import sqlite3
import time

# Links are bills on Ghana Parliament's website.


DB_LOCATION = sqlite3.connect('bills.db')


def getBillList(page):
    """
    Gets list of bills on each page.
    """
    try:
        page = requests.get(page)
        soup = BeautifulSoup(page.text, 'html.parser')
    except ConnectionError:
        print("There is a problem with your internet connection. ")

    bills_list = soup.find(class_='pdfs table1')

    bills_list_items = bills_list.find_all(text=True)

    bills_list_items.pop(0)  # There was a space at the start of the list
    bills_list_items.pop()  # There was a space at the end of each list

    return bills_list_items


def getBillCount(pages):
    """
    Finds a list of bills on the bills website.
    """
    bill_count = 0
    for page in pages:
        try:
            bills_list_items = getBillList(page)
        except ConnectionError:
            break

        for num, item in enumerate(bills_list_items):
            if num % 2 == 0:
                bill_count = bill_count + 1

    return bill_count


def getBillInfo(pages, db_location):
    """
    Inserts info about bills from parliament.gh's website into database.
    """
    global bill_name, bill_date, bill_writer
    bill_names = []
    bill_dates = []
    bill_writers = []

    c = db_location.cursor()

    for page in pages:
        try:
            page = requests.get(page)
            soup = BeautifulSoup(page.text, 'html.parser')
        except ConnectionError:
            print("There is a problem with your internet connection. ")
            break

        bills_list = soup.find(class_='pdfs table1')

        bills_list_items = bills_list.find_all(text=True)

        bills_list_items.pop(0)  # There was a space at the start of the list
        bills_list_items.pop()  # There was a space at the end of each list

        for num, item in enumerate(bills_list_items):
            if num % 2 == 0:
                bill_names.append(item)
                bill_name = item
            else:
                match = re.search(r'\d{2}-\d{2}-\d{4}', item)
                date = datetime.strptime(match.group(), '%d-%m-%Y').date()
                # date = date.strftime('%d-%m-%Y')
                bill_dates.append(date)
                bill_date = date

                meta = list(item)
                for i in range(21):
                    meta.pop(0)
                meta = ''.join(meta)
                bill_writers.append(meta)
                bill_writer = meta

                c.execute("INSERT INTO bills VALUES (?,?,?)", (bill_name, bill_date, bill_writer))

    db_location.commit()
    db_location.close()

    return bill_names, bill_dates, bill_writers

def getBillInfo_IR(pages):
    bill_names = []
    bill_writers = []
    bill_dates = []
    count = 0
    for page in pages:
        try:
            page = requests.get(page)
            soup = BeautifulSoup(page.text, 'html.parser')
        except ConnectionError:
            print("There is a problem with your internet connection. ")
            break

        elements = soup.find_all("div", class_="artifact-title".split())

        for el in elements:
            name = el.get_text(strip=True)
            name = name.replace(u'\ufeff', '')
            count = count + 1
            bill_names.append(name)

        elements = soup.find_all("span", class_="author".split())
        for el in elements:
            author = el.get_text(strip=True)
            bill_writers.append(author)

        elements = soup.find_all("span", class_="date".split())
        for el in elements:
            date = el.get_text(strip=True)

            bill_dates.append(date)

    return bill_names, bill_dates, bill_writers


def findNewsCount(citi_page, joy_page):
    """
    Returns number of news articles written about bill.
    """

    citi_page = requests.get(citi_page)
    soup = BeautifulSoup(citi_page.text, 'html.parser')
    num_citi_articles = (len(soup.find_all("article")))

    joy_page = requests.get(joy_page)
    soup = BeautifulSoup(joy_page.text, 'html.parser')
    num_joy_articles = (len(soup.find_all(class_="col-xs-6")))

    return num_citi_articles + num_joy_articles



