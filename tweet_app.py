pip install snscrape

import streamlit as st

import re
import snscrape.modules.twitter as sntwitter 
import pandas as pd 

import matplotlib.pyplot as plt 
from wordcloud import WordCloud, STOPWORDS

st.set_page_config('Tweets Dashboard')

st.title("Tweets Dashboard")
st.markdown('A simple project that fetch data from Twitter and represents data. Feel free to use :)')
st.markdown('##')

#user input

username = st.text_input('Enter Username', placeholder=('If @username, type "username"'), help=('Leave blank if you are using the Advance Search'))
adv = st.text_input('Advance Search', placeholder=("Leave empty if not in use"), help=('Same as twitter search function'))
number_tweets = st.number_input('Insert Number of Tweets', step=1,min_value=1)

pressed = st.button('Enter')
st.markdown('---')

if pressed:  
    if adv == '' and username == '':
        st.error('Please Enter Username or Advance search again', icon="🚨")
        st.stop()
    if adv != '':
        query = adv
    else:
        query = "(from:" + username + ")"
        
#    st.text(query)
    
    limit_tweets = number_tweets
    tweets = []

    for tweet in sntwitter.TwitterSearchScraper(query).get_items():
        
        if len(tweets) == limit_tweets:
            break 
        else: 
            tweets.append([tweet.date, tweet.user.username, tweet.rawContent])
            
    df = pd.DataFrame(tweets, columns=['Date', 'Username', 'Tweet'])
    
    if df.empty:
        st.error('The content does not exist, please type again', icon="🚨")
        st.stop()
    
#    st.header('Tweets Data')
#    st.dataframe(df)

#most mentioned
    
    txt = ""
    mentioned = []

    for i in df.Tweet:
        val = re.findall("@\w+", i)

        for item in val:
            txt += ' ' + item
    
        mentioned.append(txt)
    mentionedLast = mentioned[-1]
    mentionedSplit = mentionedLast.split(' ')
    mentionedSplit.pop(0)
    
    mentioned_table = pd.DataFrame(mentionedSplit, columns=['Mentioned'])
    mentioned_table_count = pd.crosstab(index=mentioned_table['Mentioned'], columns="count")
    tweet_mentioned = mentioned_table_count.sort_values(by=['count'], ascending=False)
    
#    st.header('Most Mentioned')
#    st.dataframe(tweet_mentioned)

#layout
    col1, col2 = st.columns([3,3])
    
    with col1:
        st.header('Tweets Data')
        st.dataframe(df[['Username', 'Tweet', 'Date']])
        
        #download data
        st.download_button(
            label="Download data as CSV",
            data= df.to_csv().encode('utf-8'),
            file_name='tweet_data.csv',
            mime='text/csv',
        )
        st.warning('it will rerun the program if you click Download button', icon="⚠️")
    
    with col2:
        st.header('Most Mentioned')
        st.dataframe(tweet_mentioned)

    st.markdown('---')
#line graph 

    date_data = pd.to_datetime(df['Date']).dt.date
    df_date = date_data.groupby(date_data).size().reset_index(name='count')
    
    plt.figure().set_figwidth(10)

    x = df_date['Date']
    y = df_date['count']

    plt.plot(x,y)
    
#    plt.fill(x,y)

    plt.title('Tweet Trend', fontsize=14)
    plt.xlabel('Date', fontsize=14)
    plt.ylabel('Counted Tweets', fontsize=14)

    st.header('Tweet Trend')
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.pyplot(plt.show())
    
    st.markdown('---')

#wordcloud

    tweets_no_mention = []

    for i in df.Tweet:
        txt = re.sub("@\w+", "", i)
        tweets_no_mention.append(txt)
    
    df['MentionRemove'] = tweets_no_mention
    new_data = df.drop(columns=['Tweet'])
    
    comment_words = ''
    stopwords = set(STOPWORDS)

    for val in new_data.MentionRemove:
    
        val = str(val)
        tokens = val.split()
    
        for i in range(len(tokens)):
            tokens[i] = tokens[i].lower()
    
        comment_words += " ".join(tokens) + " "
    
    wordcloud = WordCloud(width = 1000,
                     height = 1000,
                     background_color = 'white',
                     stopwords = stopwords,
                     min_font_size =  10).generate(comment_words)

    plt.figure(figsize = (5,5), facecolor = None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad = 0)

    st.header('Word Cloud')
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.pyplot(plt.show())
    
    
