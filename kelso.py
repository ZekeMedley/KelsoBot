import json
from watson_developer_cloud import NaturalLanguageUnderstandingV1
import watson_developer_cloud.natural_language_understanding.features.v1 as Features
import tweepy
from tweepy.api import API
import random
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
	return 'Hello World!'

port = os.getenv('VCAP_APP_PORT', '8080')
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=int(port))

kelsoChoices = ['making a deal', 'waiting and cooling off', 'going to another game', 'talking it out', 'sharing and taking turns', 'ignoring it', 'walking away', 'telling them to stop', 'apologizing']
openings = ['Consider', 'Try', 'I\'d suggest', 'I\'d recommend', 'How about']
start = ['Whoa!', 'Yikes!', 'Darn.']
conflictStatement = ['Don\'t get so angry at', 'It looks like you have a problem with', 'It looks like you have a conflict with', 'You\'re getting pretty mad at']

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
        print("Watson had trouble analyzing : {}".format(text))
        kelsoReady = True
        return ""

    # if we found keywords in the text
    if len(response['keywords']):
        # if there is a strong anger in the text
        if 'emotion' in response['keywords'][0].keys():
            if response['keywords'][0]['emotion']['anger'] > 0.25:
                target = [response['keywords'][0]['text']]

                try:
                    response = natural_language_understanding.analyze(
                    text= text,
                    features=[Features.Sentiment(targets = target)])
                except:
                    print("Watson had trouble analyzing : {}".format(text))
                    kelsoReady = True
                    return ""

                #if the anger is directed towards the keyword
                if (response['sentiment']['targets'][0]['score'] < -0.5):
                    with open('tweetFile.txt', 'a', encoding="utf-8") as tweetFile:
                        tweetFile.write(text)
                    kelsoReady = True
                    return response['sentiment']['targets'][0]['text']
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

        reply = getReply(unworkedTweets[wheresKelso].text)
        
        retweeted = unworkedTweets[wheresKelso].retweeted

        if len(reply) > 1 and retweeted is not None and not retweeted:
            screenName = unworkedTweets[wheresKelso].user.screen_name
            screenName = "@{} ".format(screenName)
            reply = "{} {} {} {}. {} {}. #kelsowheel".format(screenName, random.choice(start), random.choice(conflictStatement), reply, random.choice(openings), random.choice(kelsoChoices)) 
            print(reply)
            if len(reply) < 150:
                tweetId = unworkedTweets[wheresKelso].id_str
                api.update_status(status=reply, in_reply_to_status_id=tweetId)
                print("sent a tweet")
