# Kwesi Afrifa, Jun-Jul 2020, kwesi@mit.edu
# A list of miscellaneous functions used within the main program.
import re
import datetime
from datetime import datetime


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def billToSearchTerm(bill_name):
    """
    converts bill name to internet search term, i.e: ghana bills to ghana+bills
    :param bill_name: str
    :return: str
    """
    word_list = re.sub("[^\w]", " ", bill_name).split()
    # Above line taken from https://stackoverflow.com/questions/6181763/converting-a-string-to-a-list-of-words

    if len(word_list) >= 6:
        search_term = "+".join(word_list[0:5])
    else:
        search_term = "+".join(word_list)

    return search_term


# Removes the year from bill name.
def justBillName(bill_name):
    word_list = re.sub("[^\w]", " ", bill_name).split()

    if len(word_list) > 1:
        bill_name = " ".join(word_list[0: (len(word_list) - 1)])
    else:
        bill_name = " ".join(word_list)


def try_parsing_date(text):
    """
    formats input date; tries several different date formats.
    :param text: scraped date
    :return: formatted date
    """
    for fmt in ('%Y-%m-%d', '%Y-%m', '%Y'):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            pass
    raise ValueError('no valid date format found')


def removeExtras(bill_name):
    """
    removes extra text in bill names, i.e: "Pdf" or "2020" for creating hashtags
    :param bill_name: str
    :return: list
    """
    years = ["2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "201"]
    forbidden_words = ["and", "or", "And", "Or", "AND", "OR"]
    word_list = re.sub("[^\w]", " ", bill_name).split()

    for word in word_list:
        try:
            if int(word):
                word_list.pop(word_list.index(word))
        except ValueError:
            if word in years or word in forbidden_words or word == "Amendment" or word == "Pdf":
                word_list.pop(word_list.index(word))

    return word_list


def createHashtag(bill_name):
    """
    creates hashtag from bill name
    :param bill_name: str
    :return: str
    """
    hashtag = ""
    word_list = removeExtras(bill_name)

    if len(word_list) <= 3:
        hashtag = "".join(word_list)
    else:
        for word in word_list:
            if word != "Bill":
                hashtag += word[0]
            else:
                hashtag += "Bill"

    tweet_hashtag = ("https://twitter.com/intent/tweet?button_hashtag=" + hashtag + "&ref_src=twsrc%5Etfw")

    return tweet_hashtag


def mail_validate(email):
    """
    mail validation code, regex taken from:
    :param email: text
    :return: bool
    """
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False
    else:
        return True


def print_with_datetime(s):
    print("[" + str(datetime.datetime.now()) + "]", s)


def standardize(input):
    """
    removes stop words from input
    param input: str
    return: str
    """
    stop_words = ["(Mrs.)", "(Mp)", "Mrs", "Mrs.", "(Miss)", "Mr", "Dr", "Mr.", "Dr.", "hon", "hon.", "for", "of",
                  "and", "bill", "the", "on", "to", "a", "about", "an", "by"]

    inputs = input.split('_')

    for word in inputs:
        if word in stop_words:
            inputs.remove(word)

    return ' '.join(inputs)


def range_validate(num, type):
    final_array = []

    if type == "year":
        trans_dict = {'START': 2000, 'END': 2021}
    elif type == "news_hits":
        trans_dict = {'START': 1, 'END': 50}

    try:
        num = int(num)
        return [num]
    except ValueError:
        nums = num.split("_")

        for num_range in nums:
            start, end = None, None
            num_range = num_range.split("-")

            if isinstance(num_range[0], int) and isinstance(num_range[1], int):
                for num in range(num_range[0], num_range[1] + 1):
                    if str(num) in final_array:
                        continue
                    final_array.append(str(num))
            else:

                if num_range[0] == "START":
                    start = trans_dict["START"]

                if num_range[1] == "END":
                    end = trans_dict["END"]

                if not start:
                    start = int(num_range[0])

                if not end:
                    end = int(num_range[1])

                for num in range(start, end + 1):
                    if str(num) in final_array:
                        continue
                    final_array.append(str(num))

        return final_array




