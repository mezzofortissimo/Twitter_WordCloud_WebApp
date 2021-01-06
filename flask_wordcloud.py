#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import twitterwordcloud
import io

app = Flask(__name__)

@app.route("/", methods=['POST','GET'])
def submit_username():
  if request.method == 'POST':
    username = request.form['username']
    startdate = request.form['startdate']
    enddate = request.form['enddate']
    frequency = request.form['frequency']
    jsonl = request.form['jsonl'].lower()
    csv = request.form['csv'].lower()
    
    if len(frequency) == 0:
      frequency = 26
    if len(jsonl) == 0 or jsonl != "true":
      jsonl = "false"
    if len(csv) == 0 or csv != "true":
      csv = "false"

    return redirect(url_for('twitter', user = username, start = startdate, end = enddate, frequency = frequency, jsonl = jsonl, csv = csv))
  return render_template('input_username.html')

@app.route("/twitter/<user> <start> <end> <frequency> <jsonl> <csv>")
def twitter(user, start, end,  frequency, jsonl, csv):
  #return f'User: {user}  Start: {start}  End: {end}'
  
  #return "User: {} Start: {} End: {} Frequency: {} Jsonl: {} CSV: {}".format(user, start, end, frequency, jsonl, csv)
  myimage = twitterwordcloud.main(user, start, end, frequency, jsonl, csv)

  return render_template("cloud.html", w_cloud=myimage, name=user, start=start, end=end)

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0')