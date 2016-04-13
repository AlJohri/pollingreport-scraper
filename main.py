import os
from scrape import scrape_page

# Only works with "Detailed Trend", "Detailed Polls", "Complete Trend"

blacklisted_urls = [
    # Can't parse "Summary Tables"
    "http://www.pollingreport.com/CongJob.htm", # congress job ratings
    "http://www.pollingreport.com/obama_job.htm", # obama job ratings
    "http://www.pollingreport.com/BushJob.htm", # bush job ratings

    # Fails Code
    "http://www.pollingreport.com/obama_job1.htm", # Obama Gallup Tracking Job Rating
    "http://www.pollingreport.com/obama_job1a.htm" # Obama Gallup Tracking Job Rating
]

urls = [

    # Favorability Specific Pages
    "http://www.pollingreport.com/BushFav.htm", # George W. Bush (page 1)
    "http://www.pollingreport.com/bushfav2.htm", # George W. Bush (page 2)
    "http://www.pollingreport.com/clinton1.htm", # Bill Clinton
    "http://www.pollingreport.com/obama_fav.htm", # Obama

    # # Obama Job Ratings
    "http://www.pollingreport.com/obama_job2.htm",

    # Bush Job Ratings
    "http://www.pollingreport.com/BushJob1.htm",
    "http://www.pollingreport.com/bushjob2.htm",
    "http://www.pollingreport.com/bushjob3.htm",

    # Clinton Job Ratings
    "http://www.pollingreport.com/clinton-.htm",

    # Political Figure Pages
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
    "http://www.pollingreport.com/S-Z.htm",

    # Congressional Job Ratings
    "http://www.pollingreport.com/CongJob1.htm",
    "http://www.pollingreport.com/cong_dem.htm",
    "http://www.pollingreport.com/cong_rep.htm",

    # Party Approval
    "http://www.pollingreport.com/dem.htm",
    "http://www.pollingreport.com/rep.htm",
]

if __name__ == '__main__':

    os.makedirs("parsed", exist_ok=True)
    os.makedirs("raw", exist_ok=True)

    for url in urls:
        filename = url.split("/")[-1] + ".csv"
        with open("parsed/" + filename, "w", encoding="latin-1") as f:
            scrape_page(url, f)
