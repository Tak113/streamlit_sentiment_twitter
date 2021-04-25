import streamlit as st
from flair.models import TextClassifier
from flair.data import Sentence
import numpy as np
global tagger

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

@st.cache(allow_output_mutation=True)
def load_flair():
	return TextClassifier.load('en-sentiment')


tagger = load_flair()
model_load_state = st.text('Loading model, this is prototype and takes a min...')
model_load_state.text('Loading model...done!')


############################################################
# single tweet

st.write('Single tweet classification')
input_sent = st.text_input('Type your tweet', 'I love Tokyo!')

s = Sentence(input_sent)
tagger.predict(s)

st.write('Your sentence is ', str(s.labels))