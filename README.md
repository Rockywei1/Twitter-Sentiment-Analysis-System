# X.AI Twitter Sentiment Analysis

This project is a **Twitter Sentiment Analysis System** built using Streamlit, Plotly, and yFinance. It helps to analyze the sentiment of tweets from specific Twitter accounts over time and compare it with the Bitcoin price. The sentiment analysis system visualizes sentiment trends and allows for the download of tweets with associated sentiment scores in CSV format.

## Features

- **Sentiment Score Visualization**: Analyze and display the sentiment score of tweets from multiple Twitter accounts. 
- **Bitcoin Price Chart**: Fetch and display Bitcoin's historical prices for a selected date range.
- **Sentiment Score Distribution**: Generate a pie chart to visualize the distribution of sentiment scores across various categories (e.g., Extremely Bullish, Neutral, Bearish, etc.).
- **Zone Highlighting**: Add highlighted zones for different sentiment ranges (e.g., Bearish, Bullish) on the sentiment score line chart.
- **Data Export**: Export tweet data along with the calculated sentiment scores and labels to a CSV file.

## Installation

To run this project locally, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/twitter-sentiment-analysis.git
   cd twitter-sentiment-analysis
   
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt

4. Run the Streamlit app:
   ```bash
   streamlit run app.py

6. Optionally, if you're behind a proxy, set up your proxy (replace 33210 with your port number):
    ```bash
   os.environ['https_proxy'] = 'http://127.0.0.1:33210'

## Project Structure
```bash
├── app.py                # Main application file
├── sentiment_analyzer.py  # Sentiment analysis module
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

## Usage

# Adding a Twitter Account

Enter the Twitter handle of the account you'd like to analyze (without the '@' symbol) and click Add Tweets.

The system will fetch recent tweets from the account and perform sentiment analysis on them.

# Selecting Date Range

Use the Start Date and End Date inputs to filter both the sentiment scores and Bitcoin price data to your desired time range.

# Visualizing Bitcoin Prices

The system will fetch Bitcoin prices using the yFinance API and display a line chart showing Bitcoin’s performance over time for the selected date range.

# Sentiment Score Chart

After adding one or more Twitter accounts, the sentiment score chart will display the sentiment trend for each account over time, with an Overall score if multiple accounts are added.

The chart includes colored zones for different sentiment ranges (e.g., Extremely Bearish, Neutral).

# Downloading Data

After tweets are analyzed, you can download the data (tweet content, sentiment scores, and labels) in CSV format by clicking the Download Tweet Data button.

# Libraries and Dependencies

This project makes use of the following libraries:

- **Streamlit**: Framework for building data applications.

- **Plotly**: Visualization library for interactive charts.

- **yFinance**: Yahoo Finance API for fetching stock and cryptocurrency data.

- **Tweety**: Python library for fetching tweets from Twitter.

- **Pandas**: Data manipulation and analysis library.

## Support Me with Cryptocurrency

If you'd like to support me with cryptocurrency, you can donate using the QR code below:

![Donate with Cryptocurrency](https://github.com/Rockywei1/Twitter-Sentiment-Analysis-System/blob/main/QR-CODE.jpg?raw=true)

Feel free to scan the QR code with your wallet app!

