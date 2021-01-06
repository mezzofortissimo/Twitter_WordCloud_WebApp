#!/usr/bin/env python3

import os
import os.path
import sys
import csv
from datetime import datetime, timedelta
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

def convert_dates():
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

def filter_tweets(tweet, word_filter, symbol_filter):
  new_string = ""
  uninteresting_words = word_filter
  punctuations = symbol_filter
  #word_frequency = {}
  for word in tweet.lower().split():
    if word.isalpha():
      if word not in uninteresting_words:
        if "http" not in word:
          if word == "im":
            word = word.replace("m","")
          if word in word_frequency:
            word_frequency[word] += 1
          else:
            word_frequency[word] = 1

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
                if new_string in word_frequency:
                  word_frequency[new_string] += 1
                else:
                  word_frequency[new_string] = 1
 # print(word_frequency)
  #return word_frequency

def scrape_tweets():
  user = args['user']
  startdate, enddate = convert_dates()

  if args['jsonl']:
    filename = "raw_{0}-{1}-{2}.json".format(user, startdate, enddate)
    if not os.path.isfile(filename):
      os.system("snscrape --jsonl --since {1} twitter-search 'from:{0} until:{2}' > raw_{0}-{1}-{2}.json".format(user, startdate, enddate))
  else:
    filename = os.popen("snscrape --jsonl --since {1} twitter-search 'from:{0} until:{2}'".format(user, startdate, enddate)).read()

  myimage = make_wordcloud(filename)
  plt.figure(figsize = (16,9), facecolor='k')
  plt.imshow(myimage, interpolation='nearest')
  plt.axis('off')
  #plt.savefig("{0}-{1}-{2}.png".format(user, startdate, enddate), facecolor='k', bbox_inches='tight', dpi=750)
  #myimage = make_wordcloud(filename)
  img = io.BytesIO()
  plt.savefig(img,facecolor='k', bbox_inches='tight', dpi=750)
  img.seek(0)
  string = base64.b64encode(img.read())
  #image_64 = 'data:image/png;base64,' + urllib.parse.quote(string)
  image_64 = string.decode('utf-8')
  #print(type(image_64))
  return image_64
  #return myimage
  

def make_wordcloud(filename):
#  word_frequency = {}
#  new_string = ""
  #punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
  punctuations = string.punctuation
  uninteresting_words = ["the", "a", "to", "if", "is", "it", "of", "and", "or", "an", "as", "me", "my",
    "our", "ours", "you", "your", "yours", "him", "his", "her", "hers", "its",
    "their", "what", "which", "who", "whom", "this", "that", "am", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "but", "at", "by", "with", "from", "when", "where", "how",
    "all", "any", "both", "each", "few", "more", "some", "such", "nor", "too", "very", "just",
    "th","am","pm","s","t","on","in","for","so","while","let", "because", "there", "", "going", "like", "would","","than","doing","w",
    "yet","mr","ms","mrs","will","also","said","http"]

  if args['jsonl']:
    with open(filename) as f:
      for item in json_lines.reader(f):
        retweet=item['retweetedTweet']
        quoted=item['quotedTweet']
        tweet=item['content']
        if retweet==None and quoted==None:
          filter_tweets(tweet, uninteresting_words, punctuations)
  else:
    tweet_pattern = r'\"content\":\s*\"(.*?)\"\,\s*\"renderedContent\"'
    tweet_list = re.findall(tweet_pattern, filename)
    for tweet in tweet_list:
      filter_tweets(tweet, uninteresting_words, punctuations)

  final_word_frequency = {}
  for key, value in word_frequency.items():
    try:
      if value >= args['frequency']:
        final_word_frequency[key]=value
        #print(key, ' : ', value)
    except TypeError:
      print("Output {}, Type {}".format(args['frequency'], type(args['frequency'])))
  #print(final_word_frequency)

  if args['csv']:
    with open("word_list_{0}-{1}-{2}.csv".format(sys.argv[1], sys.argv[2], sys.argv[3]), 'w') as csv_file:
      writer = csv.writer(csv_file)
      for key, value in final_word_frequency.items():
        writer.writerow([key, value])

  cloud = wordcloud.WordCloud(width=1920,height=1080)
  cloud.generate_from_frequencies(final_word_frequency)
  return cloud.to_array()

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

  image = scrape_tweets()
  return image

if __name__ == '__main__':
  main()