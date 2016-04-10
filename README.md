# Polling Report Scraper

Scrapes publically available polls from [polling report](http://www.pollingreport.com/). Specifically scrapes the poll pages labeled as "detailed" ([example](http://www.pollingreport.com/obama_job2.htm)).

Because scraping Microsoft Frontpage can only be so accurate. An attempt to manually normalize the polls is here: https://docs.google.com/spreadsheets/d/1XZ_qSBlqFrsyhYzrHjljAjOHMInAMxwXlXS9b0YBVdg/edit?usp=sharing

![](http://i.imgur.com/xrrIZfZ.png)

## Setup

Requires Python 3.5+. [Anaconda](https://www.continuum.io/downloads) recommended due the numpy/pandas dependency.

```
pip install -r requirements.txt
```

## Usage

```
python scrape_pollingreport.py
```

