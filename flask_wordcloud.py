#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import twitterwordcloud
import io

app = Flask(__name__)
user_input = {}
myimage = None
gen_time = None

@app.route("/", methods=['POST','GET'])
def submit_username():
  if request.method == 'POST':
    username = request.form['username']
    startdate = request.form['startdate']
    enddate = request.form['enddate']
    frequency = request.form['frequency']
    #jsonl = request.form['jsonl'].lower()
    #csv = request.form['csv'].lower()
    filter_level = request.form['filter']
    jsonl = 'false'
    csv = 'false'
    if len(frequency) == 0:
      frequency = 26
    if len(jsonl) == 0 or jsonl != "true":
      jsonl = "false"
    if len(csv) == 0 or csv != "true":
      csv = "false"
    
    return redirect(url_for('twitter', user = username, start = startdate, end = enddate, frequency = frequency, jsonl = jsonl, csv = csv, filter_level = filter_level))

  return render_template('input_username.html')

@app.route("/twitter/<user> <start> <end> <frequency> <jsonl> <csv> <filter_level>")
def twitter(user, start, end,  frequency, jsonl, csv, filter_level):
    myimage, gen_time = twitterwordcloud.main(user, start, end, frequency, jsonl, csv, filter_level)
    return render_template("cloud.html", w_cloud=myimage, name=user, start=start, end=end, gen_time=gen_time)

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0')