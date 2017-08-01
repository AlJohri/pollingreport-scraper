# Polling Report Scraper

Normalized Polls: https://goo.gl/GRWLVH

Semi-scrapes publically available polls from [polling report](http://www.pollingreport.com/). Manual input / normalization is still required because scraping Microsoft Frontpage websites is really hard.

![](http://i.imgur.com/xrrIZfZ.png)

## Setup

Requires Python 3.6+.

```
pip install -r requirements.txt
```

## Usage

Download and parse a specific url.

```
python scrape.py http://www.pollingreport.com/BushJob1.htm
```

Downloads all of the urls listed in main.py and parses them.

```
python main.py
```
