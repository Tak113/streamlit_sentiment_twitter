# ref : https://srishti.hashnode.dev/sentiment-analysis-app-using-python-flair-and-streamlit
# ref : https://github.com/flairNLP/flair
# this version of flair (0.4.x) not work anymore
# ref : https://medium.com/analytics-vidhya/building-a-twitter-sentiment-analysis-app-using-streamlit-d16e9f5591f8

import streamlit as st
from flair.models import TextClassifier
from flair.data import Sentence
import numpy as np
import pandas as pd
global tagger
from twitterscraper import query_tweets

import datetime as dt
import re

# def load_flair():
# 	return TextClassifier.load('en-sentiment')

# def main():
# 	tagger = load_flair()

# 	st.title('Twitter Sentiment Analysis')
# 	st.write('Single tweet classification')

# 	input_sent = st.text_input('Tweet','I love Tokyo!')

# 	s = Sentence(input_sent)
# 	tagger.predict(s)
# 	st.write('### Your sentence is ', str(s.labels))

# if __name__ == '__main__':
# 	main()


st.title('Twitter Sentiment Analysis')

###########################################################
# load model

# cache management
@st.cache(allow_output_mutation=True)
def load_flair():
	return TextClassifier.load('en-sentiment')

# statement while pre trained model is loading
model_load_state = st.text('Loading pre-trained model, this is prototype and takes a min...')
tagger = load_flair()
# with st.spinner('this is a test while loading...'):
model_load_state.text('Loading pre-trained model...done!')


############################################################
# single tweet

st.subheader('Single tweet classification')

# get user input
input_tweet = st.text_input('Type your tweet:')


if input_tweet != '':
	s = Sentence(input_tweet)
	tagger.predict(s)
	st.write('Prediction:')
	st.write(s.labels[0].value + ' with ', # value is either POSITIVE or NEGATIVE
		round(s.labels[0].score * 100,1), '% confidence') # score is probability


############################################################
# scrape

st.subheader('Search twitter for query')
st.write('`twitterscraper is pulling 0 query result now, changing to API-based scraping and still under dev..`')


# get user input
query = st.text_input('Type `#query`:', '#')

# as long as the query is valid (not empty or equal to '#')...
if query != '' and query != '#':
	with st.spinner(f'Searching and analyzing {query}...'):
		
		# get english tweets from the past 4 weeks
		tweets = query_tweets(query,
			begindate = dt.date.today() - dt.timedelta(weeks=1),
			lang = 'en')

		# initialize empty dataframe
		tweet_data = pd.DataFrame({
			'tweet': [],
			'predicted-sentiment': []
		})

		# keep track of positive vs negative tweets
		pos_vs_neg = {'POSITIVE': 0, 'NEGATIVE': 0}

		# add data for each tweet
		for tweet in tweets:
			# skip iteration if tweet is empty
			if tweet.text in ('', ' '):
				continue
			# make predictions
			sentence = Sentence(tweet.text)
			tagger.predict(sentence)
			# keep track of positive vs negative tweets
			pos_vs_neg[sentiment.value] += 1 # value is either POSITIVE or NEGATIVE
			# append new data
			tweet_data = tweet_data.append({'tweet': tweet.text,
				'predicted-sentiment': sentiment}, ignore_index=True)

# show query data and sentiment if available
try:
	st.write(tweet_data)
	try:
		st.write('Positive to negative tweet ratio:', pos_vs_neg['POSITIVE']/pos_vs_neg['NEGATIVE'])
	except ZeroDivisionError: # if no negative tweets
		st.write('All positive tweets')
except NameError: # if no queries have been made yet
	pass