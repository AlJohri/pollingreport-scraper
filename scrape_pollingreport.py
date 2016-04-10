import os, re, sys, requests, lxml.html

months = r"Jan\.|Feb\.|March|April|May|June|July|Aug\.|Sept\.|Oct\.|Nov\.|Dec\."

same_month_date_range = re.compile(r"(%s) (\d+)-(\d+), (\d{4})\." % months)
different_month_date_range = re.compile(r"(%s) (\d+)-(%s) (\d+), (\d{4})\." % (months, months))
single_date = re.compile(r"(%s) (\d+), \d{4}\." % months)

from blessings import Terminal
t = Terminal()

def get_first(el, selector):
    selected_elements = el.cssselect(selector)
    if len(selected_elements) > 0 :
        return selected_elements[0]
    else:
        return None

def get_stripped_text(el):
    return re.sub(r'\s+', ' ', el.text_content()).strip() if el is not None else ""

def scrape_page(url):
    response = requests.get(url)
    doc = lxml.html.fromstring(response.content)

    for separator in doc.cssselect("hr[size='1'][color='#C0C0C0']"):
        parents = separator.iterancestors(tag='table')
        poll = next(parents)

        # poll_title_el = get_first(poll, "font[color='#004080']")
        # poll_title = get_stripped_text(poll_title_el)
        all_blue_text = poll.cssselect("font[color='#004080']")
        poll_title = " ".join([get_stripped_text(x) for x in all_blue_text])

        sample_size_match = re.search(r"N=([\d,]+)", poll_title)
        sample_size = sample_size_match.groups()[0].replace(",", "") if sample_size_match else None

        moe_match = re.search(r"(?:Margin of error|MoE|margin of error) ± (\d+)", poll_title)
        margin_of_error = moe_match.groups()[0] if moe_match else None

        date_match1 = same_month_date_range.search(poll_title)
        date = date_match1.groups() if date_match1 else None

        date_match2 = different_month_date_range.search(poll_title)
        date = date or (date_match2.groups() if date_match2 else None)
        
        date_match3 = single_date.search(poll_title)
        date = date or (date_match3.groups() if date_match2 else None)

        subpopulation = None
        if "registered voters nationwide" in poll_title:
            subpopulation = "rv"
        elif "likely voters nationwide" in poll_title:
            subpopulation = "lv"
        elif "adults nationwide" in poll_title:
            subpopulation = "a"

        question_el = get_first(poll, "font[color='#666666']:contains('\"')")
        question = get_stripped_text(question_el)

        all_text = get_stripped_text(poll)

        print(t.bold_white(poll_title))
        print([date, margin_of_error, sample_size, subpopulation])
        print(question)

        if any([keyword in all_text for keyword in favorability_keywords]):
            print(t.yellow("Potentially Favorability"))

        if any([keyword in all_text for keyword in approval_keywords]):
            print(t.yellow("Potentially Approval"))

        print()

favorability_keywords = ["favorable", "unfavorable"]
approval_keywords = ["approve", "disapprove", "disap- prove"]

if __name__ == '__main__':

    urls = [

        # Obama Job Ratings
        # "http://www.pollingreport.com/obama_job1.htm", # Gallup Daily Tracking (don't use)
        # "http://www.pollingreport.com/obama_job1a.htm", # Gallup Daily Tracking (don't use)
        "http://www.pollingreport.com/obama_job2.htm",

        # Bush Job Ratings
        "http://www.pollingreport.com/BushJob1.htm",
        "http://www.pollingreport.com/bushjob2.htm",
        "http://www.pollingreport.com/bushjob3.htm"

        # Clinton Job Ratings
        "http://www.pollingreport.com/clinton-.htm",

        # Favorability Specific Pages
        "http://www.pollingreport.com/obama_fav.htm", # Obama
        "http://www.pollingreport.com/BushFav.htm", # George W. Bush (page 1)
        "http://www.pollingreport.com/bushfav2.htm", # George W. Bush (page 2)
        "http://www.pollingreport.com/clinton1.htm", # Bill Clinton

        # Political Figure Pages
        "http://www.pollingreport.com/A-B.htm", # includes George H. W. Bush
        "http://www.pollingreport.com/c.htm", # includes Jimmy Carter
        "http://www.pollingreport.com/hrc.htm", # Hillary Clinton
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

    for url in urls:
        print(t.bold_magenta("Scraping {}".format(url)))
        scrape_page(url)
