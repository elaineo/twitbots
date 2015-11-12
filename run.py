from TwitterAPI import TwitterAPI
from semantic_tools import *
import logging


### Bot details for responding

# innocuousegg0
CONSUMER_KEY  = 'BRTo6TbrQldeU4H1wgIXez2xL'
CONSUMER_SECRET = 'OaUIDWPl39qGePIKCkzgIHpdRGpSMwJxZ5cMmTTggV4RaorUnh'
ACCESS_TOKEN =  '3267543349-FuwX6GwmS9aO1WXDK66L6WwcegfXc44Yy0gCujR'
ACCESS_TOKEN_SECRET = 'iSa1dCTP8d9ewSA22SKPMFieVGUHP8b7851uTdvSaSlTR'
botname = '@innocuousegg0'
bot_id = 3267543349

### A user to follow
user_id = 1698640628
twittername = 'george_the_egg'

## this is filename prefix used during blogparser
username = 'innocuousegg0'


###############

# preprocess if running for the first time. Comment this out later.
# 256 is the minimum number of features. Depends on complexity of training data. 
# Try 512 if the bot sucks
preprocess(username, 256)

logger = logging.getLogger(username)

### either change the location of the logs, or comment out the next four lines
hdlr = logging.FileHandler('/var/www/html/logs/' +botname[1:]+'.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

while True:
    try:
        logger.info('start')
        bot_api = TwitterAPI(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        start_it_up(logger, bot_api, username, twittername, user_id, botname, str(bot_id), delay=0)
    except:
        logger.info('restart')
        continue
