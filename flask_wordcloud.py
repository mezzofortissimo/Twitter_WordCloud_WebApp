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
    filterlevel = request.form['filter']
    jsonl = 'false'
    csv = 'false'
    if len(frequency) == 0:
      frequency = 26
    if len(jsonl) == 0 or jsonl != "true":
      jsonl = "false"
    if len(csv) == 0 or csv != "true":
      csv = "false"
    #user_input['username'] = request.form['username']
    #user_input['startdate'] = request.form['startdate']
    #user_input['enddate'] = request.form['enddate']
    #user_input['frequency'] = request.form['frequency']
    #user_input['jsonl'] = 'false'
    #user_input['csv'] = 'false'

    #if len(user_input['frequency']) == 0:
    #  user_input['frequency'] = 26
    #if len(user_input['jsonl']) == 0 or user_input['jsonl'] != "true":
    #  user_input['jsonl'] = "false"
    #if len(user_input['csv']) == 0 or user_input['csv'] != "true":
    #  user_input['csv'] = "false"
    

    return redirect(url_for('twitter', user = username, start = startdate, end = enddate, frequency = frequency, jsonl = jsonl, csv = csv))

    #return render_template('redirect.html')
  return render_template('input_username.html')

#@app.route("/loading")
#def load_word_cloud():
#  myimage, gen_time = twitterwordcloud.main(user_input['username'], user_input['startdate'], user_input['enddate'], user_input['frequency'] , user_input['jsonl'], user_input['csv'])

#  return myimage, gen_time

@app.route("/twitter/<user> <start> <end> <frequency> <jsonl> <csv>")
#@app.route("/twitter")
def twitter(user, start, end,  frequency, jsonl, csv):
#def twitter():
    myimage, gen_time = twitterwordcloud.main(user, start, end, frequency, jsonl, csv)
    return render_template("cloud.html", w_cloud=myimage, name=user, start=start, end=end, gen_time=gen_time)
    #return render_template("cloud.html", w_cloud=myimage, name=user_input['username'], start=user_input['startdate'], end=user_input['enddate'], gen_time=gen_time)

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0')