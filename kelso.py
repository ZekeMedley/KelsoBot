import json
from watson_developer_cloud import NaturalLanguageUnderstandingV1
import watson_developer_cloud.natural_language_understanding.features.v1 as \
    Features
import tweepy
from tweepy.api import API

class MyStreamListener(tweepy.StreamListener):

    global unworkedTweets

    def on_status(self, status):
        unworkedTweets.append(status)

def getReply(text):

    global kelsoReady

    try:
        response = natural_language_understanding.analyze(
        text= text,
        features=[Features.Keywords(emotion=True)])
    except:
        print("watson had a problem that's not too big. we'll ignore it and move on")
        kelsoReady = True
        return ""

    # if we found keywords in the text
    if len(response['keywords']):
        # if there is a strong anger in the text
        if 'emotion' in response['keywords'][0].keys():
            if response['keywords'][0]['emotion']['anger'] > 0.25:
                target = [response['keywords'][0]['text']]

                response = natural_language_understanding.analyze(
                text= text,
                features=[Features.Sentiment(targets = target)])

                #if the anger is directed towards the keyword
                if (response['sentiment']['targets'][0]['score'] < -0.5):
                    kelsoReady = True
                    return "please stop being so mean to {}".format(response['sentiment']['targets'][0]['text'])
    kelsoReady = True
    return ""

natural_language_understanding = NaturalLanguageUnderstandingV1(
    version='2017-02-27',
    username = "42cbe0b9-694e-418c-8a3e-a18fa597ec9b",
    password = "XnS2O1wh5ZuT")

consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret = ''

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)
myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener)

unworkedTweets = []

myStream.filter(track=['Trump'], async = True)

wheresKelso = -1
kelsoReady = True

while True:
    # if the array is getting dangerously big
    if (len(unworkedTweets) > 500000000):
        for i in range(5000000):
            del unworkedTweets[-1]

    if len(unworkedTweets) > 0 and  kelsoReady:
        kelsoReady = False
        wheresKelso += 1
        try:
            reply = getReply(unworkedTweets[wheresKelso].text)

        except:
            print("watson had a problem that was kinda big.. if we pretend it didn't happen it might go away")
        
    if len(reply) > 1 and retweeted is not None and not retweeted:
            screenName = unworkedTweets[wheresKelso].user.screen_name
            temp = "@{} ".format(screenName)
            reply = temp + reply
            print(reply)
            tweetId = unworkedTweets[wheresKelso].id_str
            print(tweetId)
            #api.update_status(status=reply, in_reply_to_status_id=tweetId)
            print("sent a tweet")
