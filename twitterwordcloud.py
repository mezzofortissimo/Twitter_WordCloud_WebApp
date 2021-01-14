#!/usr/bin/env python3

import os
import os.path
import sys
import csv
from datetime import datetime, timedelta, date
import json_lines
import json
import wordcloud
import numpy as np
from matplotlib import pyplot as plt
from IPython.display import display
import io
import re
import string
import urllib, base64
import sqlite_db as sql
import codecs
import html
#import datetime
from collections import Counter
import time


def start_timer(): #working
  start_time = time.time()
  return start_time
def check_timer(start_time): #working
  check_time = round(time.time() - start_time, 4)
  return check_time

def convert_dates(): #working
  startdate = datetime.strptime(args['start'], "%Y-%m-%d").date()

  if args['end']:
    enddate = datetime.strptime(args['end'], "%Y-%m-%d").date()
  else:
    _ = re.match(r'\d+', args['time'])
    n = int(_[0])
    if "day" in args['time']:
      _date = startdate + timedelta(days=n)
    elif "week" in args['time']:
      _date = startdate + timedelta(weeks=n)
    elif "month" in args['time']:
      if n >= 12:
        _y = ((n // 12) * 365)
        _r = (n % 12) * 31
        _date = startdate + timedelta(days=(_y + _r))
      else:
        _date = startdate + timedelta(days=(n*31))
    elif "year" in args['time']:
      _date = startdate + timedelta(days=(n*365))
    enddate = datetime.strptime(str(_date), "%Y-%m-%d").date()

  return startdate, enddate

punctuations = string.punctuation
filter_1 = ["the", "a", "to", "if", "is", "it", "of", "and", "or", "an", "as", "me", "my",
    "our", "ours", "you", "your", "yours", "him", "his", "her", "hers", "its",
    "their", "what", "which", "who", "whom", "this", "that", "am", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "but", "at", "by", "with", "from", "when", "where", "how",
    "all", "any", "both", "each", "few", "more", "some", "such", "nor", "too", "very", "just",
    "th","am","pm","s","t","on","in","for","so","while","let", "because", "there", "", "going", "like", "would","","than","doing","w",
    "yet","mr","ms","mrs","will","also","said","http"]

def filter_tweets(_dict, level):
  

  _d = _dict
  if level == 1:
    for _word in filter_1:
      if _word in _d.keys():
        _d.pop(_word)
  elif level == 2:
    for _word in filter_2:
      if _word in _d.keys():
        _d.pop(_word)
  elif level == 3:
    for _word in filter_3:
      if _word in _d.keys():
        _d.pop(_word)
  else:
    return _dict
  return _d

def old_filter_tweets(tweet, word_filter, symbol_filter):
  temp_dict = {}
  new_string = ""
  uninteresting_words = word_filter
  punctuations = symbol_filter
  for word in tweet.lower().split():
    if word.isalpha():
      if word not in uninteresting_words:
        if "http" not in word:
          if word == "im":
            word = word.replace("m","")
          if word in temp_dict:
            temp_dict[word] += 1
          else:
            temp_dict[word] = 1

    else:
      for symbol in punctuations:
        if symbol in word:
          if "#" not in word and "@" not in word and "&" not in word:
            if "'s" in word:
              new_string = word.replace("'s","")
            else:
              new_string = "".join([char for char in word if char.isalpha()])
            if "http" not in new_string:
              if new_string == "im":
                new_string = new_string.replace("m","")

              if new_string not in uninteresting_words:
                if new_string in temp_dict:
                  temp_dict[new_string] += 1
                else:
                  temp_dict[new_string] = 1
  return temp_dict

def clean_up_tweets(tweet):
  temp_dict = {}
  for word in tweet.lower().split():
    split_words = []

    if "\\n\\n" in word:
      n_1, n_2 = word.split("\\n\\n", maxsplit=1)    
      split_words.append(bytes(n_1, 'utf-8').decode("unicode_escape"))
      split_words.append(bytes(n_2, 'utf-8').decode("unicode_escape"))
    else:
      split_words.append(bytes(word, 'utf-8').decode("unicode_escape"))
    
    for words in split_words:
      if "@" in words:
        words = words.replace(words, "")
      if "http" in word:
        words = words.replace(words, "")
      if "#" in words:
        words = words.replace(words, "")
      if "amp" == words:
        words = words.replace(words, "")
      if not words.isalpha():
        for punct in string.punctuation:
          if punct in words:
            w_1, w_2 = words.split("{}".format(punct), maxsplit=1)
            words = ""
            if not w_1.isalpha():
              w_1 = "".join([char for char in w_1 if char.isalpha()])
            if not w_2.isalpha():
              w_2 = "".join([char for char in w_2 if char.isalpha()])
      if len(words) > 0 and words.isalpha():
        if words in temp_dict:
          temp_dict[words] += 1
        else:
          temp_dict[words] = 1
      else:
        if 'w_1' and 'w_2' in locals():
          if len(w_1) > 0 and w_1.isalpha():
            if w_1 in temp_dict:
              temp_dict[w_1] += 1
            else:
              temp_dict[w_2] = 1
          if len(w_2) > 0 and w_2.isalpha():
            if w_2 in temp_dict:
              temp_dict[w_2] += 1
            else:
              temp_dict[w_2] = 1
  return temp_dict

def scrape_tweets(user, startdate, enddate):
  db_dict, _list = sql.retrieve_table_data(user, startdate, enddate)
  scrape_count = int(len(_list)/2)
  loaded_count = int(len(db_dict))
  print("Database checked: {} word counts loaded; Scrapes to be executed: {} [{}s]".format(loaded_count, scrape_count, check_timer(timer)))
  count = 0
  raw_string = ""
  for dates in _list:
    if count % 2 == 0:
      print("Scraping from {} to {} [{}s]".format(_list[count], _list[count + 1], check_timer(timer)))
      _s = _list[count]
      _e = _list[count + 1]
      raw_string = raw_string + os.popen("snscrape --jsonl --since {1} twitter-search 'from:{0} until:{2}'".format(user, _s, _e + timedelta(days=1))).read()
    count += 1
  if scrape_count > 0:
    print("Scraping Complete [{}s]".format(check_timer(timer)))

  #print(raw_string)
  return raw_string, db_dict

def process_raw_tweet_data(raw_data):
  pattern = '\"url\":\s*\S*{}\s*\S*\s*\"date\": \"(\d*-\d*-\d*)[\s*\S*]*?\"content\": \"([\s*\S*]*?)\"renderedContent\"'.format(args['user'])
  tweet_ = re.findall(pattern, raw_data)
  #print(tweet_)
  #print("Tweet Tuples", tweet_) good
  dated_list = []
  count = 0

  for _ in tweet_:
    if count == 0:
      new_string = ""
      _date = _[0]
    if _date == _[0]:
      new_string = new_string + _[1]
    else:

      _dict = clean_up_tweets(new_string)

      dated_list.append(("'{}'".format(_date), _dict))
      _date = _[0]
      new_string = _[1]
    count += 1
    if count == len(tweet_):


      _dict = clean_up_tweets(new_string)

      dated_list.append(("'{}'".format(_date), _dict))
      dated_list.sort()
  if len(tweet_) > 0:
    print("Raw Twitter Data Processed [{}s]".format(check_timer(timer)))
  update_database(args['user'], dated_list)
  return dated_list

def update_database(user, data):
  for item in data:
    sql.add_data_to_row(user, item[0], item[1])
    if item[0] in full_date_range:
      full_date_range.remove(item[0])
  for date in full_date_range:
    sql.add_data_to_row(user, date, {'n/a':1})
  if len(data) > 0:
    print("Updated {} rows in table: {} [{}s]".format(len(data), user, check_timer(timer)))
    post_size = round((os.stat('twitter_users').st_size)/1000000, 2)
    print("The database is now {}mb after adding {}mb".format(post_size, post_size - pre_size))

def combine_dictionaries(dict_list, db_dict):
  new_dict = {}
  for row in dict_list:
    new_dict = dict(Counter(row[1]) + Counter(new_dict))
  new_dict = dict(Counter(db_dict) + Counter(new_dict))
  final_dict = filter_tweets(new_dict, 1)
  return final_dict

def create_wordcloud(wc_data_source):
  print("Processing Word Cloud [{}s]".format(check_timer(timer)))
  cloud = wordcloud.WordCloud(width=1920,height=1080)
  cloud.generate_from_frequencies(wc_data_source)

  myimage = cloud.to_array()

  plt.figure(figsize = (16,9), facecolor='k')
  plt.imshow(myimage, interpolation='nearest')
  plt.axis('off')
  img = io.BytesIO()
  plt.savefig(img,facecolor='k', bbox_inches='tight', dpi=750)
  plt.close('all')
  img.seek(0)
  string = base64.b64encode(img.read())
  image_64 = string.decode('utf-8')
  print("Word Cloud Generated [{}s]".format(check_timer(timer)))
  return image_64

def main(user, start, end, frequency, jsonl, csv):
  global word_frequency
  word_frequency ={}

  keys = [user, start, end, frequency, jsonl, csv]
  global args
  args = {key: None for key in keys}
  args['user'] = user
  args['start'] = start
  args['end'] = end
  
  frequency = int(frequency)
  args['frequency'] = frequency
  args['jsonl'] = False
  args['csv'] = False

  start, end = convert_dates()

  print(start, end)
  _s = datetime.strptime(args['start'], '%Y-%m-%d').date()
  _e = datetime.strptime(args['end'], '%Y-%m-%d').date()
  global full_date_range
  full_date_range = []
  while _s <= _e:
    full_date_range.append("'{}'".format(_s.strftime('%Y-%m-%d')))
    _s = _s + timedelta(days=1)
  #print(full_date_range)

  global timer
  timer = start_timer()
  sql.connect_to_database('twitter_users')
  global pre_size
  pre_size =round((os.stat('twitter_users').st_size)/1000000, 2)
  raw_tweet_data, db_dict = scrape_tweets(args['user'], args['start'], args['end'])
  scraped_dict = process_raw_tweet_data(raw_tweet_data)
  wc_ready_dict = combine_dictionaries(scraped_dict, db_dict)
  image = create_wordcloud(wc_ready_dict)
  sql.close()

  return image, round(check_timer(timer), 2)

if __name__ == '__main__':
  main(user, start, end, frequency, jsonl, csv)