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

#punctuations = string.punctuation

def load_word_filter(level):
  pronouns = False
  with open("filters/extras.txt", "r") as f:
    word_filter = f.read().splitlines() 
  
  if not level == "0":
    if level == "1":
      _ = "level1_100.txt"
    elif level == "2":
      _ = "level2_500.txt"
      pronouns = True
    elif level == "3":
      _ = "level3_1000.txt"
      pronouns = True
    with open("filters/" + _, "r") as f:
        word_filter.extend(f.read().splitlines())
    if pronouns:
      with open("filters/pronouns.txt", "r") as f:
        word_filter.extend(f.read().splitlines())

  return word_filter

def filter_tweets(_dict, filter_level):
  _d = _dict
  word_filter = load_word_filter(filter_level)
  
  for _word in word_filter:
    if _word in _d.keys():
      _d.pop(_word)
  return _d

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

  return raw_string, db_dict

def process_raw_tweet_data(raw_data):
  pattern = '\"url\":\s*\S*{}\s*\S*\s*\"date\": \"(\d*-\d*-\d*)[\s*\S*]*?\"content\": \"([\s*\S*]*?)\"renderedContent\"'.format(args['user'])
  tweet_ = re.findall(pattern, raw_data)
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

      dated_list.sort(key=lambda tup: tup[0])
      
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
  final_dict = filter_tweets(new_dict, args['filter_level'])
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

def main(user, start, end, frequency, jsonl, csv, filter_level):
  global word_frequency
  word_frequency ={}

  keys = [user, start, end, frequency, jsonl, csv, filter_level]
  global args
  args = {key: None for key in keys}
  args['user'] = user
  args['start'] = start
  args['end'] = end
  
  frequency = int(frequency)
  args['frequency'] = frequency
  args['jsonl'] = False
  args['csv'] = False
  args['filter_level'] = filter_level

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
  main(user, start, end, frequency, jsonl, csv, filter_level)