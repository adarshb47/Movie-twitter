from flask import Flask
from flask import request
from flask import render_template
from datetime import time
import sys
import csv
import tweepy
import matplotlib.pyplot as plt

from collections import Counter
from aylienapiclient import textapi

consumer_key = "THKOdLevAZ1uBS9rb9P8oT82G"
consumer_secret = "3qIN3zOgiTZ6iVUm3Rz1axhFWFGvqRtZdUZNbAYtZ1wP8PX443"
access_token = "916628957608292359-ffBg9rkYkq8Iy2hzY0IjzOz1Z4zMFgj"
access_token_secret = "NnCCDjrgFEjm5xuTP9Gao00eOgVqvVwZRUE5Xt7vycf86"

## AYLIEN credentials
application_id = " f915b41d"
application_key = "1fe6aac4ecf1b4e455b969c95c127859"

## set up an instance of Tweepy
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

## set up an instance of the AYLIEN Text API
client = textapi.Client(application_id, application_key)



application = app = Flask(__name__)

query=""
number=""

@app.route("/",methods=['GET','POST'])
def main():
    if request.method=='GET':
        return render_template('index.html')
    query = request.form['query']
    number = request.form['num']
    results = api.search(
       lang="en",
       q=query + " -rt",
       count=number,
       result_type="recent"
    )

    print("--- Gathered Tweets \n")

    ## open a csv file to store the Tweets and their sentiment
    file_name = 'Sentiment_Analysis_of_{}_Tweets_About_{}.csv'.format(number, query)

    with open(file_name, 'w', newline='') as csvfile:
       csv_writer = csv.DictWriter(
           f=csvfile,
           fieldnames=["Tweet", "Sentiment"]
       )
       csv_writer.writeheader()

       print("--- Opened a CSV file to store the results of your sentiment analysis... \n")

    ## tidy up the Tweets and send each to the AYLIEN Text API
       for c, result in enumerate(results, start=1):
           tweet = result.text
           tidy_tweet = tweet.strip().encode('ascii', 'ignore')

           if len(tweet) == 0:
               print('Empty Tweet')
               continue

           response = client.Sentiment({'text': tidy_tweet})
           csv_writer.writerow({
               'Tweet': response['text'],
               'Sentiment': response['polarity']
           })

           print("Analyzed Tweet {}".format(c))

    ## count the data in the Sentiment column of the CSV file
    with open(file_name, 'r') as data:
       counter = Counter()
       for row in csv.DictReader(data):
           counter[row['Sentiment']] += 1

       positive = counter['positive']
       negative = counter['negative']
       neutral = counter['neutral']

    ## declare the variables for the pie chart, using the Counter variables for "sizes"
    colors = ['green', 'red', 'grey']
    sizes = [positive, negative, neutral]
    labels = 'Positive', 'Negative', 'Neutral'

    ## use matplotlib to plot the chart
    plt.pie(
       x=sizes,
       shadow=True,
       colors=colors,
       labels=labels,
       startangle=90
    )


    
    return render_template('pie_chart.html',title=query,num=number, max=17000, set=zip(sizes, labels, colors))


@app.route("/simple_chart")
def chart():
    legend = 'Monthly Data'
    labels = ["January", "February", "March", "April", "May", "June", "July", "August"]
    values = [10, 9, 8, 7, 6, 4, 7, 8]
    return render_template('chart.html', values=values, labels=labels, legend=legend)


# @app.route("/line_chart")
# def line_chart():
#     legend = 'Temperatures'
#     temperatures = [73.7, 73.4, 73.8, 72.8, 68.7, 65.2,
#                     61.8, 58.7, 58.2, 58.3, 60.5, 65.7,
#                     70.2, 71.4, 71.2, 70.9, 71.3, 71.1]
#     times = ['12:00PM', '12:10PM', '12:20PM', '12:30PM', '12:40PM', '12:50PM',
#              '1:00PM', '1:10PM', '1:20PM', '1:30PM', '1:40PM', '1:50PM',
#              '2:00PM', '2:10PM', '2:20PM', '2:30PM', '2:40PM', '2:50PM']
#     return render_template('line_chart.html', values=temperatures, labels=times, legend=legend)


if __name__ == "__main__":
    app.run(debug=True)
