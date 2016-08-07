from selenium import webdriver
from time import sleep
from datetime import datetime
from bs4 import BeautifulSoup

# URL = "https://twitter.com/search?f=tweets&vertical=default&q=trump%20OR%20clinton%20OR%20hillary&src=typd"
URL = "https://twitter.com/search?f=tweets&vertical=default&q=cantaloupe&src=typd"


# the earliest tweet we want
SEARCH_START = datetime(2016, 1, 1, 0)  # year month day hour


def record_new_tweets():
    """record the 20 tweets from the latest lazy-load, return earliest date"""

    # 20 tweets loaded at a time
    tweets = driver.find_elements_by_css_selector('li.js-stream-item')[-20:]

    for tweet in tweets:
        thtml = tweet.get_attribute('innerHTML')
        soup = BeautifulSoup(thtml, 'html.parser')
        tweet_id = tweet.get_attribute('data-item-id').encode("utf8", "ignore")
        tweet_text = soup.find('div', {'class': 'js-tweet-text-container'}).get_text().encode("utf8", "ignore").strip()
        tweeter = soup.find('span', {'class': 'js-action-profile-name'}).get_text().encode("utf8", "ignore")

        tstamp = soup.find('span', {'class': '_timestamp'})['data-time']
        tstamp_datetime = datetime.fromtimestamp(float(tstamp))
        tstamp_date = datetime.strftime(tstamp_datetime, '%Y-%m-%d %H:%M:%S')

        outfile.write('|'.join([tweet_id, tstamp_date, tweet_text, tweeter]) + '\n')

    # update the new earliest date
    return tstamp_datetime

# got javascript to deal with infinite scroll from
# http://forumsqa.com/question/help-me-to-locate-an-weblement/
# jse.executeScript("window.scrollBy(0,1400)", "");

driver = webdriver.Firefox()

# internet here is slow
driver.implicitly_wait(20)  # seconds

driver.get(URL)


i = 0

# record the results as we get them in an outfile
outfile = open('cantaloupe_tweets.txt', 'w')

# header line
outfile.write('TWEET_ID|TSTAMP|TWEET_TEXT|TWEETER\n')

# record the initial 20 tweets:
earliest_date = record_new_tweets()

while earliest_date > SEARCH_START:

    i += 1

    # scroll the window to get more tweets
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")

    # wait for the reload
    sleep(3)

    # record tweets since last time
    earliest_date = record_new_tweets()

    print "iteration", i, "earliest date:", earliest_date

# cleanup
outfile.close()
