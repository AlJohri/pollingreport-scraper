import os
from scrape_pollingreport import scrape_page

from blessings import Terminal
t = Terminal()

urls = [

    # # Favorability Specific Pages
    "http://www.pollingreport.com/BushFav.htm", # George W. Bush (page 1)
    "http://www.pollingreport.com/bushfav2.htm", # George W. Bush (page 2)
    "http://www.pollingreport.com/clinton1.htm", # Bill Clinton
    "http://www.pollingreport.com/obama_fav.htm", # Obama

    # # Obama Job Ratings
    # "http://www.pollingreport.com/obama_job1.htm", # Gallup Daily Tracking (don't use)
    # # "http://www.pollingreport.com/obama_job1a.htm", # Gallup Daily Tracking (don't use)
    "http://www.pollingreport.com/obama_job2.htm",

    # # Bush Job Ratings
    "http://www.pollingreport.com/BushJob1.htm",
    "http://www.pollingreport.com/bushjob2.htm",
    "http://www.pollingreport.com/bushjob3.htm",

    # # Clinton Job Ratings
    "http://www.pollingreport.com/clinton-.htm",

    # # Political Figure Pages
    "http://www.pollingreport.com/hrc.htm", # Hillary Clinton
    "http://www.pollingreport.com/A-B.htm", # includes George H. W. Bush
    "http://www.pollingreport.com/c.htm", # includes Jimmy Carter
    "http://www.pollingreport.com/d.htm",
    "http://www.pollingreport.com/e-f.htm",
    "http://www.pollingreport.com/g.htm",
    "http://www.pollingreport.com/h-j.htm",
    "http://www.pollingreport.com/k.htm",
    "http://www.pollingreport.com/l.htm",
    "http://www.pollingreport.com/o.htm",
    "http://www.pollingreport.com/p.htm",
    "http://www.pollingreport.com/r.htm",
    "http://www.pollingreport.com/S-Z.htm"

]

if __name__ == '__main__':

    os.makedirs("parsed", exist_ok=True)
    os.makedirs("raw", exist_ok=True)

    for url in urls:
        print(t.bold_magenta("Scraping {}".format(url)))

        filename = url.split("/")[-1] + ".csv"
        with open("parsed/" + filename, "w", encoding="latin-1") as f:
            scrape_page(url, f)
