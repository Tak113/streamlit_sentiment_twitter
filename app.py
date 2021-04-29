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

# load TweetsGetter function from scrape_api.py
from scrape_api import TweetsGetter


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
st.write('`Using twitter API instead of generic scraping method which mostly blocks by them. Pulling 10 tweets at once(API has a strict rate limits)`')


# get user input
query = st.text_input('Type query`:', '#')

# as long as the query is valid (not empty or equal to '#')...
if query != '' and query != '#':
	with st.spinner(f'Searching and analyzing {query}...'):
		if __name__ == '__main__':
		
		    # get tweets by keyword
		    getter = TweetsGetter.bySearch(query)
		    
		    # get tweets by user (screen_name)
		    #getter = TweetsGetter.byUser('@realDonaldTrump')
		    
		    list_text = []
		    list_id = []
		    list_user_screenname = []
		    list_created_at = []
		    
		    for tweet in getter.collect(total = 10): # total is number of tweets to get
		        list_text.append(tweet['text'])
		        list_id.append(tweet['id'])
		        list_user_screenname.append(tweet['user']['screen_name'])
		        list_created_at.append(tweet['created_at'])
		
		# initialize empty dataframe
		tweet_data = pd.DataFrame({
		    'tweet': [],
		    'predicted-sentiment-value': [],
		    'predicted-sentiment-score': [],
		})
		
		# keep track of positive vs negative tweets
		pos_vs_neg = {'POSITIVE':0, 'NEGATIVE': 0}
		
		# add data for each tweet
		for tweet in list_text:
		    # skip iteration if tweet is empty
		    if tweet in ('',' '):
		        continue
		    # make predictions
		    sentence = Sentence(tweet)
		    tagger.predict(sentence)
		    # keep track of positive vs negative tweets
		    pos_vs_neg[sentence.labels[0].value] += 1 #value is either POSITIVE or NEGATIVE
		    # append new data
		    tweet_data = tweet_data.append({'tweet': tweet,
		                                    'predicted-sentiment-value': sentence.labels[0].value,
		                                   'predicted-sentiment-score': sentence.labels[0].score}, ignore_index=True)
		
		# get positive rate
		pos_rate = round(pos_vs_neg['POSITIVE']/(pos_vs_neg['NEGATIVE']+pos_vs_neg['POSITIVE'])*100,1)


# show query data and sentiment if available
try:
	st.write('check wide mode in appearance at settings to see entire tweets', tweet_data)
	try:
		st.write('POSITIVE tweet ratio:', pos_rate, '%')
	except ZeroDivisionError: # if no negative tweets
		st.write('All positive tweets')
except NameError: # if no queries have been made yet
	pass