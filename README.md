# Some stuff with bots

## Dependencies

For parsing blogs, use iPython notebook.

```
pip install ipython
```

Get the whole scipy stack, I can't remember which ones are necessary.

Ubuntu:
```
sudo apt-get install python-numpy python-scipy ipython ipython-notebook python-pandas python-sympy python-nose
sudo apt-get install libblas-dev liblapack-dev libatlas-base-dev gfortran
```

On MacOS, you can just get by with Anaconda:
```
https://www.continuum.io/downloads
```

### Other web scraping tools:

```
pip install requests
pip install beautifulsoup4
pip install selenium
```

### Semantic tools

Get the semantics library and natural language toolkit.
```
pip install --upgrade gensim
pip install nltk
```

Download the nltk packages.
```
python
>>> import nltk
>>> nltk.download()
NLTK Downloader
---------------------------------------------------------------------------
    d) Download   l) List    u) Update   c) Config   h) Help   q) Quit
---------------------------------------------------------------------------
Downloader> d

Download which package (l=list; x=cancel)?
  Identifier> punkt
    Downloading package punkt to /home/ubuntu/nltk_data...
      Unzipping tokenizers/punkt.zip.
      
Downloader> d

Download which package (l=list; x=cancel)?
  Identifier> stopwords
    Downloading package stopwords to /home/ubuntu/nltk_data...
      Unzipping corpora/stopwords.zip.

Downloader> q
True
>>> exit()
```

### Twitter
```
pip install TwitterAPI
```

## Scrape some blogs

Open blogparser.ipynb in iPython Notebook. Go through the steps to scrape data. 
Everything gets dumped in /data/


## Run this stuff 

Edit the variables in run.py

```
python run.py
```
