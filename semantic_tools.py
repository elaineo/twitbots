import gensim
from gensim import corpora, models, similarities
import nltk
import json

from collections import OrderedDict

from twitter_tools import *
import re
import random
import logging
import time

### further training
def add_docs(username, root='data'):
    with open('%s/%s-update.json' % (root,username)) as docs_file:
        update = json.load(docs_file)

    update = OrderedDict(update)
    texts = remove_stopwords(update)
    dictionary = corpora.Dictionary(texts)

    # each document will be represented by a x-D vector, where x is the number of unique tokens
    corpus0 = [dictionary.doc2bow(text) for text in texts]
    tfidf = models.TfidfModel(corpus0)
    corpus = tfidf[corpus0]

    corp_name = 'tmp'
    corpora.MmCorpus.serialize('%s/%s.mm' % (root,corp_name), corpus)
    corpus = corpora.MmCorpus('%s/%s.mm' % (root,corp_name))

    # load old docs
    documents, dictionary, lsi, index = load_docs(username, root)

    print 'updating lsi'
    # update lsi
    lsi.add_documents(corpus)
    lsi.save('%s/%s-corpus.lsi' % (root,username))

    #### update only works of we are not adding more documents to the dict or index
    # #update index
    index.add_documents(lsi[corpus])
    index.save('%s/%s-corpus.index' % (root,username))

    print 'dumping docs'
    # # update documents and dict
    documents.update(update)
    documents = OrderedDict(documents)
    with open('%s/%s-blog.json' % (root,username), 'w') as f:
        json.dump(documents, f)

    print 'updating dict'
    dictionary.add_documents(texts)
    dictionary.save('%s/%s.dict' % (root,username)) # store the dictionary, for future reference

    return

#### pre-processing
def texts_to_index(texts, num_topics=8, corp_name=None, root='data'):
    # convert tokenized sents to a vector
    dictionary = corpora.Dictionary(texts)
    # each document will be represented by a x-D vector, where x is the number of unique tokens
    corpus0 = [dictionary.doc2bow(text) for text in texts]
    tfidf = models.TfidfModel(corpus0)
    corpus = tfidf[corpus0]

    if not corp_name:
        corp_name = 'tmp'
    corpora.MmCorpus.serialize('%s/%s.mm' % (root,corp_name), corpus)
    corpus = corpora.MmCorpus('%s/%s.mm' % (root,corp_name))

    lsi = models.LsiModel(corpus, id2word=dictionary, num_topics=num_topics)
    #lsi = models.LdaModel(corpus, id2word=dictionary, num_topics=num_topics)
    index = similarities.Similarity('%s/%s.index' % (root,corp_name), lsi[corpus], num_features=corpus.num_terms) # transform corpus to LSI space and index it

    #index = similarities.MatrixSimilarity(lsi[corpus]) # transform corpus to LSI space and index it
    return dictionary, lsi, index

def preprocess(username, num_topics, root='data'):
    """ Take a big dict of blogs as input
        Generate corpus, dictionary, lsi, index
    """

    with open('%s/%s-blog.json' % (root,username)) as docs_file:
        documents = json.load(docs_file)

    # documents need to be ordered dicts - sort by date
    documents = OrderedDict(documents)

    # remove stopwords for each corpus and tokenize
    texts = remove_stopwords(documents)

    # remove words that appear only once in the corpus
    texts = remove_infreq(texts,1)

    dictionary, lsi, index = texts_to_index(texts, num_topics, '%s-corpus' % username)

    dictionary.save('%s/%s.dict' % (root,username)) # store the dictionary, for future reference
    lsi.save('%s/%s-corpus.lsi' % (root,username))
    index.save('%s/%s-corpus.index' % (root,username))

def preprocess_page(page, num_topics, custom_clean=None):
    # tokenize page into sentences
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    sents_all = sent_detector.tokenize(page.strip())
    if custom_clean:
       sents_all = custom_clean(sents_all)
    sent_generator = nltk.bigrams(sents_all)
    # sent_generator = nltk.bigrams(sent_detector.tokenize(page.strip()))

    sents = [" ".join(s) for s in sent_generator]
    # tokenize sentences into words
    texts = remove_stopwords(sents, True)

    dictionary, lsi, index = texts_to_index(texts, num_topics)

    return sents, dictionary, lsi, index

def preprocess_text(username, num_topics, root='debate'):
    """ Take a big list of sentences as input
        Generate corpus, dictionary, lsi, index
    """

    with open('%s/%s.json' % (root,username)) as docs_file:
        documents = json.load(docs_file)

    texts = remove_stopwords(documents, True)
    # remove words that appear only once in the corpus
    texts = remove_infreq(texts,1)
    dictionary, lsi, index = texts_to_index(texts, num_topics, '%s-corpus' % username, root)

    dictionary.save('%s/%s.dict' % (root,username)) # store the dictionary, for future reference
    lsi.save('%s/%s-corpus.lsi' % (root,username))
    index.save('%s/%s-corpus.index' % (root,username))

def load_docs(username, root='data'):
    """ Load documents
            Preprocessed: dictionary, corpus, index, lsi
            Archives: documents
    """
    #corpus = corpora.MmCorpus('data/%s-corpus.mm'% username)
    dictionary = corpora.Dictionary.load('%s/%s.dict' % (root,username))

    with open('%s/%s-blog.json' % (root,username)) as docs_file:
        documents = json.load(docs_file)

    documents = OrderedDict(documents)

    lsi = models.LsiModel.load('%s/%s-corpus.lsi' % (root,username))
    #index = similarities.MatrixSimilarity.load('data/%s-corpus.index' % username)
    index = similarities.Similarity.load('%s/%s-corpus.index' % (root,username))

    return documents, dictionary, lsi, index

def query_page(text, dictionary, lsi, index):
    """ clean input, turn into a query
        perform query and get index of most similar page
    """
    vec_bow = dictionary.doc2bow(text)
    vec_lsi = lsi[vec_bow] # convert the query to LSI space

    s = sorted(vec_lsi, key=lambda item: -item[1])
    # print lsi.print_topic(s[0][0])

    # perform query
    sims = index[vec_lsi] # perform a similarity query against the corpus

    # sort similarities in descending order
    sims = sorted(enumerate(sims), key=lambda item: -item[1])

    return sims


def start_it_up( logger, 
    bot_api, 
    username, 
    twittername, 
    userid,  
    botname, 
    bot_id_str, 
    delay=0, 
    num_topics=8, 
    debug=False, 
    custom_garbage=None, 
    custom_clean=None ):

    # load preprocessed docs
    documents, dictionary, lsi, index = load_docs(username)

    # open trash can
    try:
        with open('data/%s.trash' % username) as docs_file:
            trash_can = json.load(docs_file)
    except:
        trash_can = []

    r = bot_api.request('statuses/filter', {'follow':[userid], 'track':botname})
    # get friends
    friends_raw = bot_api.request('friends/ids', {'screen_name': twittername})
    friends = json.loads(friends_raw.response.text)
    friends = [f for f in friends.get("ids")]

    asleep = False
    debuggery = debug

    for tweet in r:

        try:
            t = tweet.get('text')

            skip, sleep, wake, debug, end_debug = filter_tweet(tweet, userid, botname, friends)
            id_str = tweet.get('id_str')  # tweet to reply to
            if sleep or wake or debug or end_debug:
                twit = bot_api.request('statuses/update', {'status': '@%s yes boss' % twittername, 'in_reply_to_status_id': id_str})
            if sleep:
                asleep = True
            if wake:
                asleep = False
            if debug:
                debuggery = True
            if end_debug:
                debuggery = False
            if skip or asleep or wake or debug or end_debug:
                continue

            try:
                reply_name = tweet.get('user').get('screen_name')
            except:
                reply_name = ''
            if botname not in t.lower():
                reply_name = ''
            else:
                if debuggery:
                    continue
                reply_name = '@%s ' % reply_name


            # get associated urls
            t += pull_headlines(tweet)

            # tokenize input sentence
            clean_input = clean_str(t).lower().split()
            if custom_garbage:
                clean_input = [c for c in clean_input if c not in custom_garbage]

            # get most similar post from input sentence
            #index.num_best = 3
            page_sims = query_page(clean_input, dictionary, lsi, index)

            # repeat the process on the sentences in the doc
            # sort the top 3 by newest
            keys = [documents.keys()[page_sims[0][0]], documents.keys()[page_sims[1][0]],
                     documents.keys()[page_sims[2][0]]]

            keys = sorted(keys)
            pages = [documents[keys[2]], documents[keys[1]], documents[keys[0]], documents.values()[page_sims[3][0]]]

            rtweet = None

            for page in pages:
                page_score = page_sims[pages.index(page)][1]

                if len(page) < 100:
                    continue

                # preprocess page
                try:
                    sents, tdict, tlsi, tidx = preprocess_page(page, num_topics, custom_clean)
                    # sort sentences by relevance
                    #tidx.num_best = 5
                    sims = query_page(clean_input, tdict, tlsi, tidx)
                except:
                    sents = [page]
                    sims = []

                if len(sims) > 4:
                    sample = [sents[sims[0][0]], sents[sims[1][0]], sents[sims[2][0]], sents[sims[3][0]], sents[sims[4][0]]]
                else:
                    sample = sents

                random.shuffle(sample)
                rtweet = create_tweet(sample, reply_name)
                if rtweet and rtweet not in trash_can:
                    # reply to the tweet
                    break
                else:
                    rtweet = None

            if not rtweet:
                continue

            time.sleep(delay)
            if debuggery:
                send_tweet(bot_api, rtweet, id_str, None)
            else:
                send_tweet(bot_api, rtweet, id_str, reply_name)

            trash_can.append(rtweet)
            with open('data/%s.trash' % username, 'w') as f:
                json.dump(trash_can, f)


            inp = tweet.get('text')
            inu = tweet.get('user').get('screen_name')
            logger.info(inu + ': ' + inp)
            logger.debug('text: ' + ' '.join(clean_input))
            logger.info(botname + ': ' + rtweet)
            logger.info('score: ' + str(page_score) + ', ')
            logger.info(sims[:4])
            logger.debug(sample)

        except:
            logger.warning('skip, probably error')
            continue