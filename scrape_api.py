# load libraries
import pandas as pd
from requests_oauthlib import OAuth1Session
import json
import datetime, time, sys
from abc import ABCMeta, abstractmethod

#import settings.py
import settings

# twitter api
CK = settings.API # API
CS = settings.API_SECRET # API Secret
AT = settings.ACCESS_TOKEN # Access Token
AS = settings.ACCESS_TOKEN_SECRET # Access Token Secret

# Twitter Getter Main Class
class TweetsGetter(object):
    __metaclass__ = ABCMeta
    
    def __init__(self):
        self.session = OAuth1Session(CK, CS, AT, AS) # connect to twitter API
    
    @abstractmethod
    def specifyUrlAndParams(self, keyword):
        '''
        Return URL and Parameters
        '''
    
    @abstractmethod
    def pickupTweet(self, res_text, includeRetweet):
        '''
        pull tweets from res_text, convert to array set and return
        '''
    
    @abstractmethod
    def getLimitContext(self, res_text):
        '''
        get # of limits info when start
        '''
    
    def collect(self, total = -1, onlyText = False, includeRetweet = False):
        '''
        start to get tweets
        '''
        
        # check n of limites
        self.checkLimit()
        
        # URL, parameter
        url, params = self.specifyUrlAndParams()
        # include_rts is paramter for statuses/user_timeline, can't use forsearch/tweets
        params['include_rts'] = str(includeRetweet).lower()
        
        # getting tweets
        cnt = 0
        unavailableCnt = 0
        while True:
            res = self.session.get(url, params = params)
            if res.status_code == 503:
                # 503 : Service Unavailable
                if unavailableCnt > 10:
                    raise Exception('Twitter API error %d' % res.status_code)
                
                unavailableCnt += 1
                print ('Service Unavailable 503')
                self.waitUntilReset(time.mktime(datetime.datetime.now().timetuple()) + 30)
                continue
            
            unavailableCnt = 0
            
            if res.status_code != 200:
                raise Exception('Twitter API erorr %d' % res.status_code)
                
            tweets = self.pickupTweet(json.loads(res.text))
            if len(tweets) == 0:
                # watned len(tweets) !=['count'], but seems count is maximum and can't use for classification
                # so ' == 0'
                # ref : https://dev.twitter.com/discussions/7513
                break
            
            for tweet in tweets:
                if(('retweeted_status' in tweet) and (includeRetweet is False)):
                    pass
                else:
                    if onlyText is True:
                        yield tweet['text']
                    else:
                        yield tweet
                        
                    cnt += 1
                    if cnt % 100 == 0:
                        print('%d ' % cnt)
                    
                    if total > 0 and cnt >= total:
                        return
            
            params['max_id'] = tweet['id'] - 1
            
            # confirm limitation
            # sometimes X-$Rate-Limit-Remaining is not included, so check
            if ('X-Rate-Limit_Remaining' in res.headers and 'X-Rate-Limit-Reset' in res.headers):
                if (int(res.headers['X-Rate-Limit-Remaining']) == 0):
                    self.waitUntilReset(int(res.headers['X-Rate-Limit-Reset']))
                    self.checkLimit()
                else:
                    print('not found - X-Rate-Limit-Remaining or X-Rate-Limit-Reset')
                    self.checkLimit()
            
    def checkLimit(self):
        '''
        ask limitation and wait until accessible
        '''
        unavailableCnt = 0
        while True:
            url = "https://api.twitter.com/1.1/application/rate_limit_status.json"
            res = self.session.get(url)

            if res.status_code == 503:
                # 503 : Service Unavailable
                if unavailableCnt > 10:
                    raise Exception('Twitter API error %d' % res.status_code)

                unavailableCnt += 1
                print ('Service Unavailable 503')
                self.waitUntilReset(time.mktime(datetime.datetime.now().timetuple()) + 30)
                continue

            unavailableCnt = 0

            if res.status_code != 200:
                raise Exception('Twitter API error %d' % res.status_code)

            remaining, reset = self.getLimitContext(json.loads(res.text))
            if (remaining == 0):
                self.waitUntilReset(reset)
            else:
                break
                
    def waitUntilReset(self, reset):
        '''
        sleep until reset time
        '''
        seconds = reset - time.mktime(datetime.datetime.now().timetuple())
        seconds = max(seconds, 0)
        print ('\n     =====================')
        print ('     == Exceeding Rate Limit for the API endpoint ==' % seconds)
        print ('     == waiting %d sec ==' % seconds)
        print ('     =====================')
        sys.stdout.flush()
        time.sleep(seconds + 10)  # add +10 sec just in case
    
    @staticmethod
    def bySearch(keyword):
        return TweetsGetterBySearch(keyword)
    
    @staticmethod
    def byUser(screen_name):
        return TweetsGetterByUser(screen_name)


class TweetsGetterBySearch(TweetsGetter):
    '''
    get tweets by keyward
    '''
    def __init__(self, keyword):
        super(TweetsGetterBySearch, self).__init__()
        self.keyword = keyword
    
    def specifyUrlAndParams(self):
        '''
        return URL and parameter
        '''
        url = 'https://api.twitter.com/1.1/search/tweets.json'
        params = {'q':self.keyword, 'count':100}
        return url, params
    
    def pickupTweet(self, res_text):
        '''
        pull tweets from res_text and convert to array and return
        '''
        results = []
        for tweet in res_text['statuses']:
            results.append(tweet)
        
        return results
    
    def getLimitContext(self, res_text):
        '''
        get limitation info when start
        '''
        remaining = res_text['resources']['search']['/search/tweets']['remaining']
        reset     = res_text['resources']['search']['/search/tweets']['reset']
        
        return int(remaining), int(reset)

class TweetsGetterByUser(TweetsGetter):
    '''
    get tweets by selecting user. not workign now, needs overhaul
    '''
    def __init__(self, screen_name):
        super(TweetsGetterByUser, self).__init__()
        self.screen_name = screen_name
    
    def specifyUrlAndParams(self):
        '''
        pull tweets from res_text and convert array and return
        '''
        results = []
        for tweet in res_text:
            results.append(tweet)
        
        return results
    
    def getLimitContext(self, res_text):
        '''
        get limitation info when start
        '''
        remaining = res_text['resources']['statuses']['/statuses/user_timeline']['remaining']
        reset     = res_text['resources']['statuses']['/statuses/user_timeline']['reset']

        return int(remaining), int(reset)