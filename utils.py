# Kwesi Afrifa, Jun-Jul 2020, kwesi@mit.edu
# A list of miscellaneous functions used within the main program.
import re
import datetime
from datetime import datetime
# Returns bill name in search term form. i.e: "Public Universities Bill" to "public+universities+bill"
def billToSearchTerm(word):
    word_list = re.sub("[^\w]", " ", word).split()
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
    for fmt in ('%Y-%m-%d','%Y-%m', '%Y'):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            pass
    raise ValueError('no valid date format found')


def removeExtras(bill_name):
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
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False
    else:
        return True


def print_with_datetime(s):
    print("[" + str(datetime.datetime.now()) + "]", s)