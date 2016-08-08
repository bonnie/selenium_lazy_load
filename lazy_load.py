from selenium import webdriver
from time import sleep
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# URL = "https://twitter.com/search?f=tweets&vertical=default&q=trump%20OR%20clinton%20OR%20hillary&src=typd"
BASE_URL = "https://twitter.com/search?"

# the earliest tweet we want
SEARCH_START = datetime(2016, 1, 1, 0)  # year month day hour


def load_url(until_date):
    """load a twitter search url based on time"""

    # empirically, twitter seems to go to 5pm on the day before the "until",
    # so we'll go a day farther, even though it means some overlap
    until_date = until_date + timedelta(days=1)

    # or two days, if our last tweet was later than 5pm
    if until_date.hour > 17:
        until_date = until_date + timedelta(days=1)

    until_date_string = datetime.strftime(until_date, "%Y-%m-%d")

    # start building the URL
    url = BASE_URL

    # only tweets
    url += "f=tweets&vertical=default"

    # search term
    url += "&q=cantaloupe until:" + until_date_string

    # only english
    url += "&lang=en"

    # not sure what this does, frankly
    url += "&src=typd"

    print "============Loading", url

    # using global driver
    driver.get(url)


def record_new_tweets(earliest_date):
    """record the 20 tweets from the latest lazy-load, return earliest date"""

    # record how many skipped due to repeat
    skipped = 0
    first = True

    start = datetime.now()

    html_text = driver.page_source.encode("utf8","ignore")
    soup = BeautifulSoup(html_text, 'html.parser')
    tweets = soup.find_all('li', { 'class': 'js-stream-item'})

    for tweet in tweets:
        tstamp = tweet.find('span', {'class': '_timestamp'})['data-time']
        tstamp_datetime = datetime.fromtimestamp(float(tstamp))

        if tstamp_datetime >= earliest_date:
            skipped += 1
            continue

        # okay starting f'real
        if first:
            print "skipped", skipped, "tweets"
            first = False

        tweet_id = tweet['data-item-id'].encode("utf8", "ignore")
        tweet_text = tweet.find('div', {'class': 'js-tweet-text-container'}).get_text().encode("utf8", "ignore").strip()
        tweeter = tweet.find('span', {'class': 'js-action-profile-name'}).get_text().encode("utf8", "ignore")
        tstamp_date = datetime.strftime(tstamp_datetime, '%Y-%m-%d %H:%M:%S')

        outfile.write('|'.join([tweet_id, tstamp_date, tweet_text, tweeter]) + '\n')

    # just to know when we start and stop
    outfile.write('-'*80 + '\n')

    end = datetime.now()
    print "*****parsing took ", (end - start).seconds, "seconds."
    print "***earliest_date:", tstamp_datetime
    print "*Time is now", end

    # reload the page to limit the time it takes to parse
    load_url(tstamp_datetime)

    # for the while loop condition
    return tstamp_datetime


# got javascript to deal with infinite scroll from
# http://forumsqa.com/question/help-me-to-locate-an-weblement/
# jse.executeScript("window.scrollBy(0,1400)", "");

driver = webdriver.Firefox()

# internet here is slow
driver.implicitly_wait(20)  # seconds

# the first page load
earliest_date = datetime.now()
load_url(earliest_date)

# counter of scrolldowns
i = 0

# record the results as we get them in an outfile
outfile = open('cantaloupe_tweets.txt', 'w')

# header line
outfile.write('TWEET_ID|TSTAMP|TWEET_TEXT|TWEETER\n')

# to record how long iterations take
last = datetime.now()

while earliest_date > SEARCH_START:

    now = datetime.now()
    i += 1
    print "iteration", i, "Elapsed: ", (now - last).seconds, "seconds"
    last = now

    # scroll the window to get more tweets
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")

    # wait for the reload
    sleep(2)

    if i % 100 == 0:

        # record tweets since last time
        # don't do it too frequently, since it's time consuming
        # plus we want to limit overlap
        earliest_date = record_new_tweets(earliest_date)


# cleanup
outfile.close()
