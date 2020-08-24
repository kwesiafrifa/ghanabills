import sqlite3
from updater import *
from webapp import *

webapp_context = {
        "running": True,
        "data_json": "",
    }


def main():
    PAGES = ['https://www.parliament.gh/docs?type=Bills&OT&P',
             'https://www.parliament.gh/docs?type=Bills&OT&P=14',
             'https://www.parliament.gh/docs?type=Bills&OT&P=28',
             'https://www.parliament.gh/docs?type=Bills&OT&P=3c']

    DB_LOCATION = sqlite3.connect("bills.db")


    webapp_context = {
        "running": True,
        "data_json": "",
    }
    startUpdater(DB_LOCATION, PAGES, webapp_context)
    run_webapp(DB_LOCATION, webapp_context)
    webapp_context["running"] = False


if __name__ == "__main__":
    main()
