### some test functions

import json
from semantic_tools import *
from twitter_tools import *

def live_issue(t, api):
    twit = api.request('statuses/update', {'status': t})
    print twit

def test_response(username, t, live=False, api=None):
    documents, dictionary, lsi, index = load_docs(username)
    rtweet = gen_response(documents, dictionary, lsi, index, t,[])
    if rtweet:
        print rtweet
        if live:
            twit = api.request('statuses/update', {'status': rtweet})
    else:
        print 'miss'

def gen_response(documents, dictionary, lsi, index, t, trash, limit1=True, custom_clean=None):
    # tokenize input sentence
    clean_input = clean_str(t).lower().split()

    # get most similar post from input sentence
    page_sims = query_page(clean_input, dictionary, lsi, index)

    # repeat the process on the sentences in the doc
    keys = [documents.keys()[page_sims[0][0]], documents.keys()[page_sims[1][0]],
             documents.keys()[page_sims[2][0]]]

    keys = sorted(keys)
    pages = [documents[keys[2]], documents[keys[1]], documents[keys[0]], documents.values()[page_sims[3][0]]]

    rtweet = None
    rmult = []

    for page in pages:
        if len(page) < 100:
            continue
        # preprocess page
        try:
            sents, tdict, tlsi, tidx = preprocess_page(page, num_topics, custom_clean)
            # sort sentences by relevance
            sims = query_page(clean_input, tdict, tlsi, tidx)
        except:
            sents = [page]
            sims = []

        if len(sims) > 4:
            sample = [sents[sims[0][0]], sents[sims[1][0]], sents[sims[2][0]], sents[sims[3][0]], sents[sims[4][0]]]
        else:
            sample = sents

        random.shuffle(sample)
        rtweet = create_tweet(sample, '')
        if rtweet and rtweet not in trash:
            # reply to the tweet
            if limit1:
                return rtweet
                break
            else:
                rmult.append(rtweet)
    if limit1:
        return None
    else:
        return rmult


def create_tweet(text, username):
    """ create a tweet from mult long sentences
        This process will vary by user.
     """
    # up to 2 tweets
    #maxlen = 263-2*len(username)
    maxlen = 139-len(username)
    for t in text:
        if ok_tweet(t, 40, maxlen):
            return t
        # go through again and break them up
        else:
            sents = sent_detector.tokenize(t)
            for s in sents:
                if ok_tweet(s, 40, maxlen):
                    return s
    return None

