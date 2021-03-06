import re
import tweepy
import json
import os
from textblob import TextBlob
from flask import Flask, Response

app = Flask(__name__)


######### Authentification
consumer_key = os.environ['consumer_key']
consumer_secret = os.environ['consumer_secret']

access_token = os.environ['access_token']
access_token_secret = os.environ['access_token_secret']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)


######### Functions
def clean_text(text):
    text = re.sub(r"@[A-Za-z0-9]+", "", text)
    text = re.sub(r"#", "", text)
    text = re.sub(r"RT[\s]+", "", text)
    text = re.sub(r"https?:\/\/\S+", "", text)
    return text

def get_opinion(keyword):
    sentiment_average = 0

    neutral = 0
    negative = 0
    weakly_negative = 0
    strongly_negative = 0
    positive = 0
    weakly_positive = 0
    strongly_positive = 0

    max_negative = 9999
    most_negative_tweet = ""
    max_positive = -9999
    most_positive_tweet = ""

    public_tweets = api.search(
        q=keyword,
        count="200",
        lang="en",
    )

    for tweet in public_tweets:
        tweet.text = clean_text(tweet.text)

        analysis = TextBlob(tweet.text)
        polarity = analysis.sentiment.polarity

        sentiment_average += polarity

        if polarity == 0:
            neutral += 1
        elif polarity > 0 and polarity < 0.33:
            weakly_positive += 1
        elif polarity >= 0.33 and polarity < 0.66:
            positive += 1
        elif polarity >= 0.66:
            strongly_positive += 1
        elif polarity < 0 and polarity > -0.33:
            weakly_negative += 1
        elif polarity <= -0.33 and polarity > -0.66:
            negative += 1
        elif polarity <= -0.66:
            strongly_negative += 1

        if polarity > max_positive:
            max_positive = polarity
            most_positive_tweet = tweet.text
        if polarity < max_negative:
            max_negative = polarity
            most_negative_tweet = tweet.text

    sentiment_average /= len(public_tweets)

    response = Response(
        json.dumps({
            "status":
            200,
            "keyword":
            keyword,
            "number_of_tweets":
            len(public_tweets),
            "average_sentiment":
            sentiment_average / len(public_tweets) * 100,
            "max_negative":
            max_negative,
            "most_negative_tweet":
            most_negative_tweet,
            "max_positive":
            max_positive,
            "most_positive_tweet":
            most_positive_tweet,
            "neutral":
            neutral / len(public_tweets) * 100,
            "weakly_positive":
            weakly_positive / len(public_tweets) * 100,
            "positive":
            positive / len(public_tweets) * 100,
            "strongly_positive":
            strongly_positive / len(public_tweets) * 100,
            "weakly_negative":
            weakly_negative / len(public_tweets) * 100,
            "negative":
            negative / len(public_tweets) * 100,
            "strongly_negative":
            strongly_negative / len(public_tweets) * 100
        }),
        status=200,
        mimetype="application/json",
    )

    return response


######### Routes
# Default page
@app.route("/")
def index():
    response = Response(
        json.dumps({
            "status":
            200,
            "message":
            "Api is live. Read the documentation at https://github.com/Jeusto/twitter-opinion",
        }),
        status=200,
        mimetype="application/json",
    )
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


# Redirect from short url to long url
@app.route("/<keyword>")
def return_opinion(keyword):
    response = get_opinion(keyword)

    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


# Start server
if __name__ == "__main__":
  app.run(host='0.0.0.0', port=8080)