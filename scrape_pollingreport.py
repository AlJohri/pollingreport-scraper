import os, re, sys, csv, requests, lxml.html, traceback
from collections import defaultdict
from pprint import pprint as pp
import pandas as pd
import numpy as np

pd.set_option('display.width', 1000)

months = r"Jan\.|Feb\.|March|April|May|June|July|Aug\.|Sept\.|Oct\.|Nov\.|Dec\."

same_month_date_range = re.compile(r"(%s) (\d+)-(\d+), (\d{4})\." % months)
different_month_date_range = re.compile(r"(%s) (\d+)-(%s) (\d+), (\d{4})\." % (months, months))
single_date = re.compile(r"(%s) (\d+), \d{4}\." % months)

def is_date(x):
    return bool(re.search(r"[\d-]+", x))

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

def scrape_page(url, f):
    response = requests.get(url)
    doc = lxml.html.fromstring(response.content)

    question_counter = 0

    for separator in doc.cssselect("hr[size='1'][color='#C0C0C0']"):

        try:

            parents = separator.iterancestors(tag='table')
            poll = next(parents)

            # Hack
            if "President Obama: Job Ratings" in poll.text_content(): continue

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

            qindextitle = url.split("/")[-1] + " | Question %d" % question_counter

            print(t.bold_white(qindextitle))
            print(t.bold_white(poll_title))
            print(t.yellow(question))
            print([margin_of_error, sample_size, subpopulation])
            question_counter += 1

            f.write("\"" + qindextitle + "\"" ); f.write("\n")
            f.write("\""  + poll_title + "\"" ); f.write("\n")
            f.write(question); f.write("\n")

            # if any([keyword in all_text for keyword in favorability_keywords]):
            #     print(t.yellow("Potentially Favorability"))

            # if any([keyword in all_text for keyword in approval_keywords]):
            #     print(t.yellow("Potentially Approval"))

            # Find first row after question
            question_row = next(question_el.iterancestors('tr'))
            first_data_row = question_row.getnext()
            if len(first_data_row.cssselect("td")) == 1:
                first_data_row = first_data_row.getnext()

            # TODO: parse poll properly if there is no line between question and first row
            # e.g. last 2 polls on http://www.pollingreport.com/bushfav2.htm

            # Find all rows after the question
            rows = [first_data_row] + list(first_data_row.itersiblings())

            # Remove last row if it contains an hr tag
            if rows[-1].cssselect("hr"): del rows[-1]

            num_columns = len(rows[0].cssselect("td"))

            # Ensure that all rows have the same number of columns
            if all([len(row.cssselect("td")) == num_columns for row in rows]):
            # Filter down to rows with at least 4 columns (ideally the data)
            # rows = [row for row in rows if len(row.cssselect("td")) > 4]

                # Remove first row if its entirely blank or a single dot
                if re.search(r'^\s+|\.$', rows[0].text_content().strip()): del rows[0]

                # Remove last row if its entirely blank
                if rows[-1].text_content().strip() == "": del rows[-1]

                sample_size_column_index = None

                # Remove second row if it has a percentage sign in it.
                if re.search(r'%', rows[1].text_content()):
                    if re.search(r'N', rows[1].text_content()):
                        sample_size_column_index = [i for i, x in  enumerate(rows[1].cssselect("td")) if get_stripped_text(x) == "N"][0]
                    del rows[1]

                # First row should now be the header row
                if re.search(r"Favorable|Unfavorable|Approve|Disapprove", rows[0].text_content()):
                    # continue parsing this table

                    headers = [get_stripped_text(x).lower() for x in rows[0].cssselect("td")]

                    for i, header in enumerate(headers):
                        if header == "disap- prove":
                            headers[i] = "disapprove"

                        if header == "unfav- orable":
                            headers[i] = "unfavorable"

                    if sample_size_column_index is not None:
                        headers[sample_size_column_index] = "sample_size"

                    data = []

                    for row in rows[1:]:
                        actual_row = [get_stripped_text(x) for x in row]
                        data.append(actual_row)

                    # DEBUG
                    # print(headers)
                    # pp(data)

                    df = pd.DataFrame(data, columns=headers)
                    df.replace('', np.nan, regex=True, inplace=True)

                    # Remove first column if its entirely blank
                    df.dropna(axis=1, how='all', inplace=True)

                    if is_date(df.iloc[0,0]):
                        columns = list(df.columns)
                        columns[0] = "date"
                        df.columns = columns

                    # TODO: parse out pollster from poll_title
                    # TODO: parse date into start date / end date

                    if 'sample_size' not in df:
                        df['sample_size'] = np.nan
                    else:
                        df['sample_size'] = df['sample_size'].replace(',', '', regex=True)

                    df['margin_of_error'] = np.nan
                    df['subpopulation'] = np.nan

                    df.loc[df.date.str.contains('rv', case=False).fillna(False), 'subpopulation'] = 'rv'
                    df.loc[df.date.str.contains('lv', case=False).fillna(False), 'subpopulation'] = 'lv'

                    if pd.isnull(df.ix[0, 'sample_size']):
                        df.ix[0, 'sample_size'] = sample_size or np.nan

                    if pd.isnull(df.ix[0, 'margin_of_error']):
                        df.ix[0, 'margin_of_error'] = margin_of_error or np.nan

                    if pd.isnull(df.ix[0, 'subpopulation']):
                        df.ix[0, 'subpopulation'] = subpopulation or np.nan

                    print(t.green(str(df)))

                    df['url'] = url
                    df['original'] = poll_title
                    df['question'] = question
                    df['date'] = df['date'].map(lambda x: "=\"" + x + "\"") # excel date hack
                    df['pollster'] = poll_title.split(".")[0]

                    f.write(df.to_csv(index=False))
                    f.write("\n")

            else:
                print(t.red("table could not be parsed. expecting all rows to have %d columns. offending rows:" % num_columns))
                for row in rows:
                    if len(row.cssselect("td")) != len(rows[0].cssselect("td")):
                        print("\t", [get_stripped_text(x) for x in row.cssselect("td")])

                f.write("manually enter poll"); f.write("\n")

            f.write("\n")
            f.write("\n")
            f.write("\n")
            f.write("\n")
            f.write("\n")
            print()

        except Exception as e:
            print(t.red("ERROR: " + str(e)))
            print(t.red(traceback.format_exc()))

            continue

favorability_keywords = ["favorable", "unfavorable"]
approval_keywords = ["approve", "disapprove", "disap- prove"]

if __name__ == '__main__':

    urls = [

        # # Favorability Specific Pages
        # "http://www.pollingreport.com/BushFav.htm", # George W. Bush (page 1)
        # "http://www.pollingreport.com/bushfav2.htm", # George W. Bush (page 2)
        "http://www.pollingreport.com/clinton1.htm", # Bill Clinton
        # "http://www.pollingreport.com/obama_fav.htm", # Obama

        # # Obama Job Ratings
        # # "http://www.pollingreport.com/obama_job1.htm", # Gallup Daily Tracking (don't use)
        # # "http://www.pollingreport.com/obama_job1a.htm", # Gallup Daily Tracking (don't use)
        # "http://www.pollingreport.com/obama_job2.htm",

        # # Bush Job Ratings
        # "http://www.pollingreport.com/BushJob1.htm",
        # "http://www.pollingreport.com/bushjob2.htm",
        # "http://www.pollingreport.com/bushjob3.htm",

        # # Clinton Job Ratings
        # "http://www.pollingreport.com/clinton-.htm",

        # # Political Figure Pages
        # "http://www.pollingreport.com/A-B.htm", # includes George H. W. Bush
        # "http://www.pollingreport.com/c.htm", # includes Jimmy Carter
        # "http://www.pollingreport.com/hrc.htm", # Hillary Clinton
        # "http://www.pollingreport.com/d.htm",
        # "http://www.pollingreport.com/e-f.htm",
        # "http://www.pollingreport.com/g.htm",
        # "http://www.pollingreport.com/h-j.htm",
        # "http://www.pollingreport.com/k.htm",
        # "http://www.pollingreport.com/l.htm",
        # "http://www.pollingreport.com/o.htm",
        # "http://www.pollingreport.com/p.htm",
        # "http://www.pollingreport.com/r.htm",
        # "http://www.pollingreport.com/S-Z.htm"

    ]

    with open("polls.csv", "w", encoding="latin-1") as f:
        for url in urls:
            print(t.bold_magenta("Scraping {}".format(url)))
            scrape_page(url, f)
