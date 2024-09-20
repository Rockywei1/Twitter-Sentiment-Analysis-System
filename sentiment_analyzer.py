import json
import re
from datetime import datetime
from typing import Dict, List

import pandas as pd
import streamlit as st
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from tweety.types import Tweet

# Initialize the VADER sentiment analyzer
analyzer = SentimentIntensityAnalyzer()


# Function to clean tweets by removing URLs and extra spaces
def clean_tweet(text: str) -> str:
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"www.\S+", "", text)
    return re.sub(r"\s+", " ", text)


# Function to create a dataframe from a list of tweets (showing all tweets)
def create_dataframe_from_tweets(tweets: List[Tweet]) -> pd.DataFrame:
    rows = []
    for tweet in tweets:
        clean_text = clean_tweet(tweet.text)
        if len(clean_text) == 0:
            continue
        rows.append(
            {
                "id": tweet.id,
                "text": clean_text,  # Include the tweet text for visibility
                "author": tweet.author.username,
                "date": str(tweet.date.date()),  # Keep the date as a string
                "created_at": tweet.date,
                "views": tweet.views,
            }
        )

    df = pd.DataFrame(
        rows, columns=["id", "text", "author", "date", "views", "created_at"]
    )
    df.set_index("id", inplace=True)

    # Ensure that we do not filter the tweets by date (remove the 7-day filter)
    return df.sort_values(by="created_at", ascending=False)


# Function to analyze sentiment using VADER and return daily aggregated sentiment
def analyze_sentiment(twitter_handle: str, tweets: List[Tweet]) -> Dict[str, int]:
    sentiments = {}

    # Create a dataframe of tweets for the given Twitter handle
    df = create_dataframe_from_tweets(tweets)
    user_tweets = df[df.author == twitter_handle]

    if user_tweets.empty:
        return sentiments

    # Iterate through the tweets, calculate sentiment, and store it by date
    for tweet_date, tweet_group in user_tweets.groupby("date"):
        daily_sentiment = []

        for tweet in tweet_group.itertuples():
            # Get sentiment score using VADER
            score = analyzer.polarity_scores(tweet.text)['compound']
            # Convert score to 0-100 scale (VADER returns scores between -1 and 1)
            sentiment_score = (score + 1) * 50  # Convert to range 0-100
            daily_sentiment.append(sentiment_score)

        # Average sentiment for the day
        sentiments[tweet_date] = sum(daily_sentiment) / len(daily_sentiment)

    return sentiments
