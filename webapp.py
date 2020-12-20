# Kwesi Afrifa, Jun-Jul 2020, [kwesi, adanna]@mit.edu
import flask
import json
import sqlite3
import waitress

from updater import *
from utils import *
from flask import request, jsonify


app = flask.Flask(__name__)


def run_webapp(DB_LOCATION, webapp_context):
    webapp = flask.Flask(
        __name__,
        static_url_path="",
        static_folder="static")
    webapp.config["DEBUG"] = True


    @webapp.route("/")
    def index_bypass():
        return flask.render_template("index.html")

    @webapp.route("/resources/bills/all", methods=['GET'])
    def api_all():
        DB_LOCATION.row_factory = dict_factory
        c = DB_LOCATION.cursor()
        all_bills = c.execute('''SELECT 
                                        bills.bill_name, 
                                        bills.bill_date, 
                                        bills.bill_writer, 
                                        bill_links.bill_search_link,
                                        bill_links.bill_search_link1,
                                        bill_links.bill_pdf_link,
                                        bill_links.bill_news_hits
                                        FROM bills
                                        INNER JOIN bill_links
                                        ON bills.id = bill_links.id;''').fetchall()
        return jsonify(all_bills)

    @webapp.route("/resources/bills/", methods=['GET'])
    def api_filter():
        query_parameters = request.args

        author = query_parameters.get('author')
        name = query_parameters.get('name')
        news_mentions = query_parameters.get('news_mentions')
        years = query_parameters.get('years')

        query = "SELECT * FROM bills INNER JOIN bill_links ON bills.id = bill_links.id WHERE"
        to_filter = []

        if name:

            name = standardize(name)
            name_list = name.split()

            if len(name_list) > 1:
                query += "("
                for n in name_list[0:-1]:
                    query += ' bill_name LIKE ? OR'
                    to_filter.append('%' + n + '%')

            query += ' bill_name LIKE ?) AND'
            to_filter.append('%' + name_list[-1] + '%')

        if author:
            author = standardize(author)
            author_list = author.split()

            if len(author_list) > 1:
                query += "("
                for a in author_list[0:-1]:
                    query += ' bill_writer LIKE ? OR'
                    to_filter.append('%' + a + '%')

            query += ' bill_writer LIKE ?) AND'
            to_filter.append('%' + author_list[-1] + '%')

        if news_mentions:
            news_mentions_list = range_validate(news_mentions, "news_hits")

            if len(news_mentions_list) > 1:
                query += "("
                for n in news_mentions_list[0:-1]:
                    query += ' bill_news_hits LIKE ? OR'
                    to_filter.append(n)

            query += ' bill_news_hits LIKE ?) AND'
            to_filter.append(news_mentions_list[-1])

        if years:
            years_list = range_validate(years, "year")

            if len(years_list) > 1:
                query += "("
                for y in years_list[0:-1]:
                    query += ' bill_date LIKE ? OR'
                    to_filter.append('%' + y + '%')

            query += ' bill_date LIKE ?) AND'
            to_filter.append('%' + years_list[-1] + '%')

        if not (author or name or news_mentions or years):
            return

        query = query[:-4] + ';'

        DB_LOCATION.row_factory = dict_factory
        c = DB_LOCATION.cursor()

        results = c.execute(query, to_filter).fetchall()
        print(query)
        return jsonify(results)

    @webapp.route("/data.json")
    def send_data():
        return flask.Response(
            webapp_context["data_json"],
            mimetype="application/json")

    @webapp.route("/bills")
    def bills():
        return flask.render_template("bills.html")

    @webapp.route("/about", methods=["POST", "GET"])
    def about():
        if request.method == 'POST':
            body = request.form.get('body')  # Access the data inside the text box
            name = request.form.get('name')
            mail_issue(name, body)

        return flask.render_template("about.html")

    @webapp.route("/forum", methods=['POST', 'GET'])
    def forum():
        bill_name = request.args.get('bill')
        bill_name = str(bill_name)

        return flask.render_template("forum.html", title=bill_name)

    @webapp.route("/subscribe/count.json")
    def get_sub_count():
        c = DB_LOCATION.cursor()
        response = json.dumps(c.execute(
            "SELECT COUNT(*) FROM subscribers;"
        ).fetchone()[0])
        DB_LOCATION.commit()
        DB_LOCATION.close()
        return flask.Response(response, mimetype="application/json")

    @webapp.route("/subscribe/check/<email>")
    def check_sub_email(email):
        c = DB_LOCATION.cursor()

        response = json.dumps(c.execute(
            "SELECT COUNT(*) FROM subscribers WHERE email = ?;",
            (email,)).fetchone()[0] > 0)

        DB_LOCATION.commit()
        DB_LOCATION.close()
        return flask.Response(response, mimetype="application/json")

    @webapp.route("/subscribe/toggle/<email>")
    def toggle_sub_email(email):
        c = DB_LOCATION.cursor()
        in_subscribers = c.execute(
            "SELECT COUNT(*) FROM subscribers WHERE email = ?;",
            (email,)).fetchone()[0] > 0
        c.execute(
            "DELETE FROM subscribers WHERE email = ?;"
            if in_subscribers else
            "INSERT INTO subscribers VALUES (?);",
            (email,))
        DB_LOCATION.commit()
        DB_LOCATION.close()
        response = ("Unsubscribed " if in_subscribers else "Subscribed ") \
                   + email + "."
        return flask.Response(response, mimetype="text/html")

    @webapp.route("/news_hits.json")
    def send_data1():
        DB_LOCATION = sqlite3.connect('bills.db', check_same_thread=False)
        db_cursor = DB_LOCATION.cursor()

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
                                        ON bills.id = bill_links.id ORDER BY bill_news_hits DESC;''').fetchall()

        DB_LOCATION.commit()
        DB_LOCATION.close()

        data = [{"bill_name": bill[0].title(),
                 "bill_date": bill[1],
                 "bill_writer": bill[2],
                 "bill_link": bill[3],
                 "bill_link1": bill[4],
                 "bill_pdf_link": bill[5],
                 "bill_news_hits": bill[6],
                 "bill_year": try_parsing_date(str(bill[1])).year,
                 "bill_tweet": createHashtag(bill[0].title())} for bill in bills]

        print(json.dumps(data))

        return flask.Response(
            json.dumps(data),
            mimetype="application/json")

    waitress.serve(webapp, host='0.0.0.0', port=5000)


