# Polling Report Scraper

Polls: https://docs.google.com/spreadsheets/d/1XZ_qSBlqFrsyhYzrHjljAjOHMInAMxwXlXS9b0YBVdg/edit?usp=sharing

Semi-scrapes publically available polls from [polling report](http://www.pollingreport.com/). Manual input / normalization is still required because scraping Microsoft Frontpage websites is really hard.

![](http://i.imgur.com/xrrIZfZ.png)

## Setup

Requires Python 3.5+. [Anaconda](https://www.continuum.io/downloads) recommended due the numpy/pandas dependency.

```
pip install -r requirements.txt
```

## Usage

Downloads all of the urls listed in main.py and parses them.

```
python main.py
```
