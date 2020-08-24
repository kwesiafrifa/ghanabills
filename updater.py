# Kwesi Afrifa, Jun-Jul 2020, kwesi@mit.edu
import asyncio
import smtplib
import ssl
import json
import email
import threading
import traceback

from scrape import *
from utils import *
from sqlite3 import Error
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

PAGES = ['https://www.parliament.gh/docs?type=Bills&OT&P',
         'https://www.parliament.gh/docs?type=Bills&OT&P=14',
         'https://www.parliament.gh/docs?type=Bills&OT&P=28',
         'https://www.parliament.gh/docs?type=Bills&OT&P=3c']

PAGES_IR = ['http://ir.parliament.gh/handle/123456789/283/browse?order=ASC&rpp=20&sort_by=2&etal=-1&offset=0&type=dateissued',
            'http://ir.parliament.gh/handle/123456789/283/browse?order=ASC&rpp=20&sort_by=2&etal=-1&offset=20&type=dateissued',
            'http://ir.parliament.gh/handle/123456789/283/browse?order=ASC&rpp=20&sort_by=2&etal=-1&offset=40&type=dateissued',
            'http://ir.parliament.gh/handle/123456789/283/browse?order=ASC&rpp=20&sort_by=2&etal=-1&offset=60&type=dateissued']


try:
    DB_LOCATION = sqlite3.connect('bills.db')
except Error:
    print(Error)

# Send emails indicating availability of new bills.
# Code taken from https://realpython.com/python-send-email/


def mail_new_bill(DB_LOCATION, new_bill, page):
    """
    Sends email to subscribers about new bills.
    """
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = ""  # Enter your address
    receiver_email = "" # Enter receiver address
    password = ""

    c = DB_LOCATION.cursor()
    c.execute("SELECT * FROM subscribers")
    subscribers = [
        result[0] for result in
        c.execute("SELECT * FROM subscribers;").fetchall()
    ]
    if len(subscribers) == 0:
        return

    for subscriber in subscribers:
        message = MIMEMultipart()
        message['Subject'] = "[ghanabills.com] New Bill Tabled"
        message['From'] = sender_email
        message['To'] = subscriber
        receiver_email = subscriber
        message.attach(MIMEText(
            """ <p> New bill is named: """ + new_bill + ".</p>" + "<p> Read it <a href=\"https://" + page + "\">here</a>. </p>" + "<p> Head to <a href=\"https://ghanabills.com/bills\">ghanabills.com/bills</a> to find out more! Or, <a href=\"https://ghanabills.com/subscribe/toggle/" + subscriber + "\">unsubscribe</a> from ghanabills.com :(", "html"
        ))

        print(receiver_email)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())

    print_with_datetime("Emailed " + str(len(subscribers)) + " subscribers.")




def mail_issue(name, body):
    """
    Mail issues via error form on about page.
    """
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "billsofghana@gmail.com"  # Enter your address
    receiver_email = "kwesi@mit.edu"  # Enter receiver address
    password = "Bills@ghana123"

    body = "User: " + name + "\n" + "\n" + "Issue: " + body
    message = MIMEText(body)

    message['Subject'] = 'Issue with website'
    message['From'] = sender_email
    message['To'] = receiver_email

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())


def inputNewBills(PAGES, DB_LOCATION):
    """
    Scrapes parliament.gh and inputs new bill data into the database.
    """
    is_new_bill = False
    new_bill_count = 0

    c = DB_LOCATION.cursor()

    for page in PAGES:
        bills_list_items = getBillList(page)

        for num, item in enumerate(bills_list_items):
            if num % 2 == 0:
                bill_name = item
            else:
                match = re.search(r'\d{2}-\d{2}-\d{4}', item)
                date = datetime.strptime(match.group(), '%d-%m-%Y').date()
                bill_date = date

                meta = list(item)
                for i in range(21):
                    meta.pop(0)
                meta = ''.join(meta)
                bill_writer = meta

                c.execute("SELECT 1 FROM bills WHERE bill_name = ? AND bill_date = ?", (bill_name, bill_date))

                # If the bill is already in the database....
                if c.fetchone():
                    pass
                else:
                    is_new_bill = True
                    mail_new_bill(DB_LOCATION, bill_name, page)
                    new_bill_count = new_bill_count + 1
                    c.execute("INSERT INTO bills VALUES (?,?,?)", (bill_name, bill_date, bill_writer))
                    c.execute(
                        "INSERT INTO bill_links (bill_search_link, bill_search_link1, bill_news_hits) VALUES (?, ?, ?)",
                        ("https://www.myjoyonline.com/?s="
                         + billToSearchTerm(bill_name),
                         "https://http://citifmonline.com/?s=" + billToSearchTerm(bill_name),
                         findNewsCount(
                            "https://http://citifmonline.com/?s=" + billToSearchTerm(bill_name),
                            "https://www.myjoyonline.com/?s=" + billToSearchTerm(bill_name))))

            # Soon, create a table to store the new bills. (URGENT)
    DB_LOCATION.commit()

    print(new_bill_count, "new bills.")

    return new_bill_count


def createDataJSON(db_location):
    """
    Creates data array for bills page from "bills.db" database.
    """

    db_cursor = db_location.cursor()

    bills = db_cursor.execute('''SELECT 
                                bills.bill_name, 
                                bills.bill_date, 
                                bills.bill_writer, 
                                bill_links.bill_search_link,
                                bill_links.bill_search_link1,
                                bill_links.bill_pdf_link,
                                bill_links.bill_news_hits
                                FROM bills
                                INNER JOIN bill_links
                                ON bills.id = bill_links.id ORDER BY bill_date DESC;''').fetchall()

    db_location.commit()
    db_location.close()
    print(bills)

    data = json.dumps([{"bill_name": bill[0].title(),
             "bill_date": bill[1],
             "bill_writer": bill[2],
             "bill_link": bill[3],
             "bill_link1": bill[4],
             "bill_pdf_link": bill[5],
             "bill_news_hits": bill[6],
             "bill_year": try_parsing_date(str(bill[1])).year,
             "bill_tweet": createHashtag(bill[0].title())} for bill in bills])

    print(data)
    return data

def inputNewBills_IR(PAGES, DB_LOCATION):

    is_new_bill = False
    new_bill_count = 0

    c = DB_LOCATION.cursor()


    bill_names, bill_dates, bill_writers = getBillInfo_IR(PAGES)

    for i in range(0, 58):
        bill_name = bill_names[i]
        bill_date = bill_dates[i]
        bill_writer = bill_writers[i]

        c.execute("SELECT 1 FROM bills WHERE bill_name = ? AND bill_date = ?", (bill_name, bill_date))
        print(i)
        # If the bill is already in the database....
        if c.fetchone():
            pass
        else:
            is_new_bill = True
            print(bill_name, "not in DB")
            mail_new_bill(bill_name, bill_date, 'ir.gov')
            new_bill_count = new_bill_count + 1
            c.execute("INSERT INTO bills (bill_name, bill_date, bill_writer) VALUES (?,?,?)", (bill_name, bill_date, bill_writer))
            c.execute(
                "INSERT INTO bill_links (bill_search_link, bill_search_link1, bill_news_hits) VALUES (?, ?, ?)",
                ("https://www.myjoyonline.com/?s="
                    + billToSearchTerm(bill_name),
                "https://citifmonline.com/?s=" + billToSearchTerm(bill_name),
                    findNewsCount(
                    "https://citifmonline.com/?s=" + billToSearchTerm(bill_name),
                    "https://www.myjoyonline.com/?s=" + billToSearchTerm(bill_name))))
            DB_LOCATION.commit()

            # Soon, create a table to store the new bills. (URGENT)


    print(new_bill_count, "new bills.")

    return is_new_bill, new_bill_count

def dataUpdate(DB_LOCATION):
    c = DB_LOCATION.cursor()
    try:
        bill_count = getBillCount(PAGES)
        is_new_bill, new_bill_count = inputNewBills(PAGES, DB_LOCATION)
    except ConnectionError:
        print("Your internet connection is unavailable/unstable.")
        return

    cursorObj = c.execute('SELECT * FROM bills')

    bill_table_len = len(cursorObj.fetchall())

    if bill_count != bill_table_len:
        print("Database is not correct size.")

    DB_LOCATION.close()
    return


def startUpdater(DB_LOCATION, PAGES, webapp_context):
    def update(webapp_context):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        while webapp_context["running"]:
            time.sleep(3600)
            c = DB_LOCATION.cursor()
            try:
                inputNewBills(PAGES, DB_LOCATION)
                webapp_context["data_json"] = createDataJSON(DB_LOCATION)
            except:
                traceback.print_exc()

            DB_LOCATION.commit()
            DB_LOCATION.close()

    inputNewBills(PAGES, DB_LOCATION)
    webapp_context["data_json"] = createDataJSON(DB_LOCATION)
    updater = threading.Thread(
        target=update,
        args=(webapp_context,)
    )
    updater.daemon = True
    updater.start()

