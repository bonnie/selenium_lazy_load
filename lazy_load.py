from selenium import webdriver
from time import sleep
from datetime import datetime

# URL = "https://twitter.com/search?f=tweets&vertical=default&q=trump%20OR%20clinton%20OR%20hillary&src=typd"
URL = "https://twitter.com/search?f=tweets&vertical=default&q=cantaloupe&src=typd"


# the earliest tweet we want
SEARCH_START = datetime(2016, 8, 2, 21) # year month day hour

# got javascript to deal with infinite scroll from
# http://forumsqa.com/question/help-me-to-locate-an-weblement/
# jse.executeScript("window.scrollBy(0,1400)", "");

driver = webdriver.Firefox()

# internet here is slow
driver.implicitly_wait(20) # seconds

driver.get(URL)

# track whether we've reached the start of our search
# for now, we'll assume the earliest tweet we've seen so far is now
earliest_date = datetime.now()

i = 0


while earliest_date > SEARCH_START:

  print "iteration", i
  i += 1

  # scroll the window to get more tweets
  driver.execute_script("window.scrollBy(0,1400)")

  # wait for the reload
  sleep(5)

#   # if it didn't reload because of slowness
#   if :
#     <a role="button" href="#" class="try-again-after-whale">Try again</a>
#     continue

  # update earliest date
  # <span class="_timestamp js-short-timestamp js-relative-timestamp" data-time="1470197337" data-time-ms="1470197337000" data-long-form="true" aria-hidden="true">14h</span>
  new_date = driver.find_elements_by_class_name('_timestamp')[-1]
  new_tstamp = float(new_date.get_attribute('data-time')) # fromtimestamp requires a float
  earliest_date = datetime.fromtimestamp(new_tstamp)

  print "new earliest date", earliest_date


# get the text and parse with beautiful soup
# text = driver.page_source.encode("utf8","ignore")

#         <div class="js-tweet-text-container">
