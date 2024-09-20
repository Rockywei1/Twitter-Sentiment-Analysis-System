# Import the necessary libraries
import os
from datetime import datetime
from typing import Dict

import pandas as pd
import plotly.express as px
import streamlit as st
import yfinance as yf

from tweety.bot import Twitter
from sentiment_analyzer import analyze_sentiment
import csv
from io import StringIO

# Proxy setup if needed (comment out if not used) Change 33210 to your own vpn terminal
os.environ['https_proxy'] = 'http://127.0.0.1:33210'

# Twitter client
twitter_client = Twitter()

# Streamlit page config
st.set_page_config(
    layout="centered",
    page_title="X.AI Twitter Sentiment Analysis",
    page_icon="https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f4c8.png",
)

# Add a centered title to the page
st.markdown(
    """
    <style>
    .title {
        font-size: 40px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
    <div class="title">Sentiment Analysis System Made By X.AI</div>
    """,
    unsafe_allow_html=True
)

# Function to add a Twitter author
def on_add_author():
    twitter_handle = st.session_state.twitter_handle
    if twitter_handle.startswith("@"):
        twitter_handle = twitter_handle[1:]
    if twitter_handle in st.session_state.twitter_handles:
        return
    all_tweets = twitter_client.get_tweets(twitter_handle)
    if len(all_tweets) == 0:
        return
    st.session_state.twitter_handles[twitter_handle] = all_tweets[0].author.name
    st.session_state.tweets.extend(all_tweets)

    # Update sentiment data for each author
    st.session_state.author_sentiment[twitter_handle] = analyze_sentiment(
        twitter_handle, all_tweets
    )

# Create sentiment DataFrame
def create_sentiment_dataframe(sentiment_data: Dict[str, Dict[str, int]]) -> pd.DataFrame:
    dates = set()
    for author_data in sentiment_data.values():
        dates.update(author_data.keys())
    dates = sorted(list(dates))
    chart_data = {"date": dates}
    for author, author_sentiment in sentiment_data.items():
        author_sentiment_values = []
        for date in dates:
            author_sentiment_values.append(author_sentiment.get(date, None))
        chart_data[author] = author_sentiment_values
    sentiment_df = pd.DataFrame(chart_data)
    sentiment_df.set_index("date", inplace=True)

    # Ensure the index is in datetime format
    sentiment_df.index = pd.to_datetime(sentiment_df.index)

    if not sentiment_df.empty:
        sentiment_df["Overall"] = sentiment_df.mean(axis=1, skipna=True)
    return sentiment_df

# Function to categorize sentiment scores into labels
def categorize_sentiment(sentiment_scores):
    labels = []
    for score in sentiment_scores:
        if score >= 80:
            labels.append("Extremely Bullish")
        elif score >= 55:
            labels.append("Bullish")
        elif score >= 30:
            labels.append("Neutral")
        elif score >= 20:
            labels.append("Bearish")
        else:
            labels.append("Extremely Bearish")
    return labels

# Function to create a pie chart for sentiment distribution
def display_sentiment_distribution_pie(sentiment_df):
    # Get the overall sentiment scores
    if 'Overall' in sentiment_df.columns:
        overall_sentiment_scores = sentiment_df['Overall'].dropna()
        sentiment_labels = categorize_sentiment(overall_sentiment_scores)
        sentiment_label_counts = pd.Series(sentiment_labels).value_counts()

        # Set the opacity level
        opacity_level = 0.4  # Adjust this value between 0 (fully transparent) and 1 (fully opaque)

        # Create the pie chart with RGBA colors for opacity control
        pie_fig = px.pie(
            names=sentiment_label_counts.index,
            values=sentiment_label_counts.values,
            title="Sentiment Score Distribution",
            color=sentiment_label_counts.index,
            color_discrete_map={
                "Extremely Bullish": f"rgba(255, 0, 0, {opacity_level})",  # red with opacity
                "Bullish": f"rgba(255, 165, 0, {opacity_level})",  # orange with opacity
                "Neutral": f"rgba(0, 0, 255, {opacity_level})",  # blue with opacity
                "Bearish": f"rgba(173, 216, 230, {opacity_level})",  # lightblue with opacity
                "Extremely Bearish": f"rgba(0, 128, 0, {opacity_level})",  # green with opacity
            }
        )
        st.plotly_chart(pie_fig, theme="streamlit", use_container_width=True)


# Fetch Bitcoin price data using yfinance
def fetch_bitcoin_price_data(start_date, end_date):
    bitcoin_data = yf.download("BTC-USD", start=start_date, end=end_date.strftime('%Y-%m-%d'))
    bitcoin_data['Date'] = bitcoin_data.index
    bitcoin_data.reset_index(drop=True, inplace=True)
    return bitcoin_data[['Date', 'Close']]

# Initialize session states
if "tweets" not in st.session_state:
    st.session_state.tweets = []
    st.session_state.twitter_handles = {}
    st.session_state.author_sentiment = {}

# Date picker to select a start and end date for filtering data
st.markdown("<h3>Select Date Range</h3>", unsafe_allow_html=True)
col1, col2 = st.columns(2)
start_date = col1.date_input("Start date", datetime(2017, 1, 1))
end_date = col2.date_input("End date", datetime.today())

# Add Twitter accounts and fetch tweets
with st.container():
    st.markdown("<h3>Add Twitter Account</h3>", unsafe_allow_html=True)
    col3, col4 = st.columns([3, 1])

    with col3:
        with st.form(key="twitter_handle_form", clear_on_submit=True):
            st.text_input("Twitter Handle", value="", key="twitter_handle", placeholder="")
            submit = st.form_submit_button(label="Add Tweets", on_click=on_add_author)

    with col4:
        if st.session_state.twitter_handles:
            st.markdown("<h4>Twitter Handles</h4>", unsafe_allow_html=True)
            for handle, name in st.session_state.twitter_handles.items():
                handle = "@" + handle
                st.markdown(f"{name} ([{handle}](https://twitter.com/{handle}))")

# Fetch Bitcoin price data using the selected date range
bitcoin_data = fetch_bitcoin_price_data(start_date, end_date)

# Create the sentiment dataframe
sentiment_df = create_sentiment_dataframe(st.session_state.author_sentiment)

# Plot Bitcoin price chart
if not bitcoin_data.empty:
    bitcoin_fig = px.line(
        bitcoin_data,
        x='Date',
        y='Close',
        title="Bitcoin Price Over Time",
        labels={"Close": "Bitcoin Price"},
        markers=False,
        line_shape='linear'
    )
    st.plotly_chart(bitcoin_fig, theme="streamlit", use_container_width=True)

# Plot sentiment score chart
if not sentiment_df.empty:
    # Ensure the index is in datetime format and filter the sentiment data by date range
    filtered_sentiment_df = sentiment_df[
        (sentiment_df.index >= pd.to_datetime(start_date)) & (sentiment_df.index <= pd.to_datetime(end_date))]

    if len(st.session_state.twitter_handles) > 1:
        columns_to_plot = list(st.session_state.twitter_handles.keys()) + ["Overall"]
    else:
        columns_to_plot = list(st.session_state.twitter_handles.keys())

    sentiment_fig = px.line(
        filtered_sentiment_df,
        x=filtered_sentiment_df.index,
        y=columns_to_plot,
        title="Sentiment Analysis For Twitter Account",
        markers=False,
        line_shape='linear'
    )

    sentiment_fig.update_traces(line=dict(width=3))

    # Color consistency between line chart and pie chart
    color_mapping = {
        "Extremely Bearish": "green",
        "Bearish": "lightgreen",
        "Neutral": "blue",
        "Bullish": "orange",
        "Extremely Bullish": "red"
    }
    opacity_level = 0.4  # Ensure the same opacity level is used across both charts

    # Add the "Extremely Bearish" zone (0-20)
    sentiment_fig.add_shape(type="rect", x0=filtered_sentiment_df.index[0], x1=filtered_sentiment_df.index[-1],
                            y0=0, y1=20, fillcolor=color_mapping["Extremely Bearish"], opacity=opacity_level,
                            layer="below", line_width=2)

    # Add the "Bearish" zone (20-30)
    sentiment_fig.add_shape(type="rect", x0=filtered_sentiment_df.index[0], x1=filtered_sentiment_df.index[-1],
                            y0=20, y1=30, fillcolor=color_mapping["Bearish"], opacity=opacity_level,
                            layer="below", line_width=2)

    # Add the "Neutral" zone (30-55)
    sentiment_fig.add_shape(type="rect", x0=filtered_sentiment_df.index[0], x1=filtered_sentiment_df.index[-1],
                            y0=30, y1=55, fillcolor=color_mapping["Neutral"], opacity=opacity_level,
                            layer="below", line_width=2)

    # Add the "Bullish" zone (55-80)
    sentiment_fig.add_shape(type="rect", x0=filtered_sentiment_df.index[0], x1=filtered_sentiment_df.index[-1],
                            y0=55, y1=80, fillcolor=color_mapping["Bullish"], opacity=opacity_level,
                            layer="below", line_width=2)

    # Add the "Extremely Bullish" zone (80-100)
    sentiment_fig.add_shape(type="rect", x0=filtered_sentiment_df.index[0], x1=filtered_sentiment_df.index[-1],
                            y0=80, y1=100, fillcolor=color_mapping["Extremely Bullish"], opacity=opacity_level,
                            layer="below", line_width=2)

    st.plotly_chart(sentiment_fig, theme="streamlit", use_container_width=True)

    # Display sentiment distribution as a pie chart
    display_sentiment_distribution_pie(sentiment_df)

# Option to download tweet data as CSV
if st.session_state.tweets:
    def export_tweets_to_csv(sentiment_df):
        export_data = []
        for tweet in st.session_state.tweets:
            tweet_id = tweet.id
            tweet_content = getattr(tweet, 'full_text', None) or getattr(tweet, 'text', None) or getattr(tweet,
                                                                                                         'content',
                                                                                                         None)
            tweet_date = getattr(tweet, 'created_at', None) or getattr(tweet, 'date', None) or getattr(tweet,
                                                                                                       'timestamp',
                                                                                                       None)

            if tweet_date is not None:
                tweet_date = pd.to_datetime(tweet_date).date()

            sentiment_score = None
            sentiment_label = "Unknown"
            if tweet_date is not None and tweet.author.screen_name in sentiment_df.columns:
                sentiment_df.index = pd.to_datetime(sentiment_df.index).date
                if tweet_date in sentiment_df.index:
                    sentiment_score = sentiment_df.loc[tweet_date, tweet.author.screen_name]
                if sentiment_score is not None:
                    if sentiment_score > 80:
                        sentiment_label = "Extremely Bullish"
                    elif sentiment_score < 20:
                        sentiment_label = "Extremely Bearish"
                    else:
                        sentiment_label = "Neutral"

            export_data.append([tweet_id, tweet_content, tweet_date, sentiment_score, sentiment_label])

        export_df = pd.DataFrame(export_data,
                                 columns=["Tweet ID", "Content", "Date", "Sentiment Score", "Sentiment Label"])
        csv_buffer = StringIO()
        export_df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()
        st.download_button(label="Download Tweet Data", data=csv_data, file_name='tweet_sentiment_data.csv',
                           mime='text/csv')


    export_tweets_to_csv(sentiment_df)
