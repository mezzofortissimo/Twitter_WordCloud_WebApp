#!/usr/bin/env python3

import sqlite3
import json
from datetime import date, timedelta, datetime
import datetime


def connect_to_database(database): #working
  conn = sqlite3.connect(database)
  print("Connection Successful")
  cur = conn.cursor()
  return conn, cur

def table_exists(name): #working
  query = "SELECT name FROM sqlite_master WHERE type='table' AND name='{}'".format(name)
  if cur.execute(query).fetchone():
    return True
  else:
    return False

def create_table(name): #working
  if not table_exists(name):
    query = 'CREATE TABLE {} (DATE TEXT PRIMARY KEY NOT NULL, DICT TEXT NOT NULL)'.format(name)
    cur.execute(query)
    conn.commit()
    print("Table Created")
  else:
    print("Table not Created")

def insert_data_to_table(table, _date, _dict): #working
  if not table_exists(table):
    create_table(table)

  _ = json.dumps(_dict)
  converted_dict = "'"+_+"'"

  query = 'INSERT INTO {} (DATE, DICT) VALUES ({}, {})'.format(table, _date, converted_dict)
  try:
    cur.execute(query)
    print("Data Added")
  except sqlite3.IntegrityError:
    print("Data not Added")
  conn.commit()

def retrieve_row_from_table(table, row): #working
  _dict = json.loads(row[1])
  _date = strip_date(row[0])
  return _date, _dict

def retrieve_table(table): #working
  query = "SELECT DATE, DICT from {} ORDER BY DATE".format(table)
  cur.execute(query)
  text=cur.fetchall()
  return text

def strip_date(date): #working
  return date.replace("'", "")

def update_dictionary(_dict, _list, table, start_date, end_date): #working  
  query = "SELECT DATE, DICT from {} WHERE DATE BETWEEN '{}' AND '{}' ORDER BY DATE".format(table, start_date, end_date)
  data = cur.execute(query)

  count = 0
  date_list = []
  for row in data:
    _date, table_dict = retrieve_row_from_table(table, row)
    _dict.update(table_dict)
    count += 1
    
    dt = datetime.datetime.strptime(_date, '%Y-%m-%d').date()
    date_list.append(dt)

  if count > 0:
    print("{} entries added to dictionary".format(count))
  else:
    print("No entries added to dictionary")

  for date in date_gaps(date_list):
    _list.append(date)  
  
def date_gaps(dates): #working
  date_gaps = []
  _ = dates
  date_set = set(_[0] + timedelta(x) for x in range((_[-1] - _[0]).days))
  missing = sorted(date_set - set(_))

  i = 0
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

def close(): #working
  conn.close()
  print("Connection Closed")

def main(): #working
  global conn, cur
  conn, cur = connect_to_database('twitter_users')

if __name__ == "__main__":
  main()