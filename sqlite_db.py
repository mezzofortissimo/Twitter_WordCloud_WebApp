#!/usr/bin/env python3

import sqlite3
import json
from datetime import date, timedelta, datetime
import datetime
from collections import Counter

############################################
# First:
#   main()
# Then: 
#   add_data_to_row(table, _date, _dict)
#     or
#   retrieve_table_data(_dict, _list, table, start_date, end_date)
# Finally:
#   close()
#############################################

def connect_to_database(database):
  global conn, cur
  #conn, cur = connect_to_database('twitter_users')
  conn = sqlite3.connect(database)
  print("Connection Successful")
  cur = conn.cursor()
  return conn, cur

def table_exists(name):
  query = "SELECT name FROM sqlite_master WHERE type='table' AND name='{}'".format(name)
  if cur.execute(query).fetchone():
    return True
  else:
    return False

def create_table(name):
  if not table_exists(name):
    query = 'CREATE TABLE {} (DATE TEXT PRIMARY KEY NOT NULL, DICT TEXT NOT NULL)'.format(name)
    cur.execute(query)
    conn.commit()
    print("Table created for user: {}".format(name))
  else:
    print("Using existing user table: {}".format(name))

def add_data_to_row(table, _date, _dict):
  if not table_exists(table):
    create_table(table)

  _ = json.dumps(_dict)
  converted_dict = "'"+_+"'"

  query = 'INSERT INTO {} (DATE, DICT) VALUES ({}, {})'.format(table, _date, converted_dict)
  try:
    cur.execute(query)
    #print("Data added to {}".format(_date))
  except sqlite3.IntegrityError:
    pass
    #print("Data not added to {}".format(_date))
  conn.commit()

def retrieve_row_from_table(table, row):
  _dict = json.loads(row[1])
  _date = strip_date(row[0])
  return _date, _dict

def retrieve_table(table):
  query = "SELECT DATE, DICT from {} ORDER BY DATE".format(table)
  cur.execute(query)
  text=cur.fetchall()
  return text

def strip_date(date):
  return date.replace("'", "")

#def retrieve_table_data(_dict, _list, table, start_date, end_date):
def retrieve_table_data(table, start_date, end_date):
  _dict = {}
  _list = []
  _start = datetime.datetime.strptime(start_date, '%Y-%m-%d').date() - timedelta(days=0)
  _end = datetime.datetime.strptime(end_date, '%Y-%m-%d').date() + timedelta(days=0)
  date_list=[]
  if table_exists(table):
    query = "SELECT DATE, DICT from {} WHERE DATE BETWEEN '{}' AND '{}' ORDER BY DATE".format(table, start_date, end_date)
    data = cur.execute(query)

    date_list=[]
    _ = {}
    for row in data:
      _date, table_dict = retrieve_row_from_table(table, row)
      _ = dict(Counter(_) + Counter(table_dict))
      dt = datetime.datetime.strptime(_date, '%Y-%m-%d').date()
      date_list.append(dt)
    _dict.update(_)
    
    for date in date_gaps(date_list, _start, _end):
      _list.append(date)
  else:
    print("Table does not exist user: {}".format(table))
    _list.extend([_start, _end])
  #return date_list
  return _dict, _list

  
def date_gaps(dates, _start, _end):
  date_gaps = []
  #print("Start", _start, "End", _end)
  _ = dates
  _.append(_start - timedelta(days=1))
  _.append(_end + timedelta(days=1))
  _.sort()
  #print("Date List", _)
  date_set = set(_[0] + timedelta(x) for x in range((_[-1] - _[0]).days))

  missing = sorted(date_set - set(_))
  #print("Missing", missing)

  i = 0
  if len(missing) == 1:
    date_gaps.append(missing[i])
    date_gaps.append(missing[i])
  if len(missing) == 2:
    date_gaps.append(missing[i])
    date_gaps.append(missing[i])
    date_gaps.append(missing[i+1])
    date_gaps.append(missing[i+1])
  elif len(missing) > 2:
    for date in missing:
      if i < len(missing) - 1:
        if i == 0:
          date_gaps.append(missing[i])
          i += 1
        else:
          x = abs(date - missing[i - 1])
          if x > timedelta(days=1):
            date_gaps.append(missing[i - 1])
            date_gaps.append(missing[i])
          i += 1
      else:
        date_gaps.append(missing[i])
  return date_gaps

def close():
  conn.close()
  print("Connection Closed")

def main():
  global conn, cur
  conn, cur = connect_to_database('twitter_users')

if __name__ == "__main__":
  main()