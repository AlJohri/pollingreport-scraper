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

    html_filename = url.split("/")[-1]
    
    if os.path.isfile("raw/" + html_filename):
        print(t.bold_magenta("Opening {}".format(url)))
        with open("raw/" + html_filename, "rb") as f2:
            response_content = f2.read()
    else:
        print(t.bold_magenta("Scraping {}".format(url)))
        response = requests.get(url)
        response_content = response.content
        with open("raw/" + html_filename, "wb") as f2:
            f2.write(response_content)

    doc = lxml.html.fromstring(response_content)

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

            # TODO: make subpopulation finding case insensitive

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

            # Find first row after question
            question_row = next(question_el.iterancestors('tr'))
            first_data_row = question_row.getnext()
            if len(first_data_row.cssselect("td")) == 1:
                first_data_row = first_data_row.getnext()

            # Find all rows after the question
            rows = [first_data_row] + list(first_data_row.itersiblings())

            # Remove last row if it contains an hr tag
            if rows[-1].cssselect("hr"): del rows[-1]

            #####################################################

            def remove_blank_first_last_rows():
                # Remove first row if its entirely blank or a single dot
                if re.search(r'^$|^\.$', rows[0].text_content().strip()): del rows[0]
                # Remove last row if its entirely blank or a single dot
                if re.search(r'^$|^\.$', rows[-1].text_content().strip()): del rows[-1]

            #####################################################

            remove_blank_first_last_rows()

            #####################################################

            highest_approval_index = None
            lowest_approval_index = None

            highest_lowest_approval_rows = []

            for i, row in enumerate(rows):

                row_text = get_stripped_text(row)

                # if its listing highest approval polls
                if "Highest approval" in row_text:
                    highest_approval_index = i

                # if its listing lowest approval polls
                if "Lowest approval" in row_text:
                    lowest_approval_index = i

            # Trim list to above highest approval_index
            if highest_approval_index is not None and lowest_approval_index is not None:
                if highest_approval_index < lowest_approval_index:
                    highest_lowest_approval_rows = rows[highest_approval_index:]
                    rows = rows[0:highest_approval_index]

            #####################################################

            remove_blank_first_last_rows()

            #####################################################

            # Dangerous to just remove all blank lines / lines with a dot
            # Could be a single question with two different sets of answers

            # rows_indexes_to_remove = []
            # for i, row in enumerate(rows):
            #     row_text = row.text_content().strip()
            #     # if its entirely blank or a single dot
            #     if re.search(r'^$|^\.$', row_text):
            #         rows_indexes_to_remove.append(i)
            # for index in sorted(rows_indexes_to_remove, reverse=True):
            #     del rows[index]

            #####################################################

            num_columns = len(rows[0].cssselect("td"))

            # Ensure that all rows have the same number of columns
            all_rows_equal = lambda: all([len(row.cssselect("td")) == num_columns for row in rows])

            # Ensure that all rows except last have the same number of columns
            # The last row may be notes with asterisks
            all_rows_except_last = lambda: all([len(row.cssselect("td")) == num_columns for row in rows[:-1]])

            last_row = None
            if not all_rows_equal() and all_rows_except_last():
                last_row = rows.pop(-1)

            if all_rows_equal():

                sample_size_column_index = None

                # Remove second row if it has a percentage sign in it.
                if re.search(r'%', rows[1].text_content()):
                    if re.search(r'N', rows[1].text_content()):
                        sample_size_column_index = [i for i, x in  enumerate(rows[1].cssselect("td")) if get_stripped_text(x) == "N"][0]
                    del rows[1]

                header_regex = r"favorable|favor- able|unfavorable|unfav- orable|positive|negative|approve|disapprove|excellent|not sure|unsure|no opinion|satisfied"

                first_row_text = get_stripped_text(rows[0])

                # First row should now be the header row
                if re.search(header_regex, first_row_text, re.IGNORECASE):
                    # continue parsing this table

                    if re.search(r"favorable|unfavorable", first_row_text, re.IGNORECASE):
                        question_type = "favorability"
                    elif re.search(r"positive|negative", first_row_text, re.IGNORECASE):
                        question_type = "thermometer"
                    elif re.search(r"approve|disapprove|excellent", first_row_text, re.IGNORECASE):
                        question_type = "approval"
                    else:
                        question_type = "unknown"

                    headers = [get_stripped_text(x).lower() for x in rows[0].cssselect("td")]

                    for i, header in enumerate(headers):
                        if header == "disap- prove":
                            headers[i] = "disapprove"

                        if header == "favor- orable":
                            headers[i] = "unfavorable"

                        if header == "unfav- orable":
                            headers[i] = "unfavorable"

                        if header == "excellent/ good":
                            headers[i] = "excellent/good"

                        if header == "fair/ poor":
                            headers[i] = "fair/poor"

                    if sample_size_column_index is not None:
                        headers[sample_size_column_index] = "sample_size"

                    data = []

                    for row in rows[1:]:
                        actual_row = [get_stripped_text(x) for x in row.cssselect("td")]
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
                    else:
                        print(t.red(str(df)))
                        print()
                        raise Exception("cannot find date in top left of dataframe")

                    # TODO: parse date into start date / end date

                    if 'sample_size' not in df:
                        df['sample_size'] = ''
                    else:
                        df['sample_size'] = df['sample_size'].replace(',', '', regex=True)

                    df['margin_of_error'] = np.nan
                    df['subpopulation'] = np.nan
                    df['question_type'] = question_type

                    # TODO remove "lv" and "rv" from the date column as well
                    #      also potentially remove asterisks and carets? maybe not

                    df.loc[df.date.str.contains('rv', case=False).fillna(False), 'subpopulation'] = 'rv'
                    df.loc[df.date.str.contains('lv', case=False).fillna(False), 'subpopulation'] = 'lv'

                    df['date'] = df.date.str.replace("lv|rv", "", case=False).str.strip()

                    df.loc[df.sample_size.str.contains('rv', case=False).fillna(False), 'subpopulation'] = 'rv'
                    df.loc[df.sample_size.str.contains('lv', case=False).fillna(False), 'subpopulation'] = 'lv'

                    df['sample_size'] = df.sample_size.str.replace("lv|rv", "", case=False).str.strip()

                    if df.ix[0, 'sample_size'] == '':
                        df.ix[0, 'sample_size'] = sample_size or np.nan

                    if pd.isnull(df.ix[0, 'margin_of_error']):
                        df.ix[0, 'margin_of_error'] = margin_of_error or np.nan

                    if pd.isnull(df.ix[0, 'subpopulation']):
                        df.ix[0, 'subpopulation'] = subpopulation or np.nan

                    print(t.green(str(df)))

                    df['url'] = url
                    df['original'] = poll_title
                    df['question'] = question
                    df['date'] = df['date'].map(lambda x: "=\"" + str(x) + "\"") # excel date hack
                    df['pollster'] = poll_title.split(".")[0]

                    f.write(df.to_csv(index=False))
                    f.write("\n")

                else:
                    print(t.red("header could not be found?"))
                    print("\t", row[0].text_content())
                    import pdb; pdb.set_trace()

            else:
                print(t.red("table could not be parsed. expecting all rows to have %d columns. offending rows:" % num_columns))
                for row in rows:
                    if len(row.cssselect("td")) != len(rows[0].cssselect("td")):
                        print("\t", [get_stripped_text(x) for x in row.cssselect("td")])

                f.write("manually enter poll"); f.write("\n")

            if last_row is not None:
                print(t.yellow("additional notes:"))
                f.write("\n"); f.write("additional notes"); f.write("\n")
                last_row_text = [get_stripped_text(x) for x in last_row.cssselect("td")]
                print("\t", last_row_text)

                f.write(str(last_row_text)); f.write("\n")

            if len(highest_lowest_approval_rows) > 0:
                print(t.yellow("highest lowest approval rows:"))
                f.write("\n"); f.write("highest lowest approval rows"); f.write("\n")
                for row in highest_lowest_approval_rows:
                    row_text = [get_stripped_text(x) for x in row.cssselect("td")]
                    print("\t", row_text)
                    f.write(str(row_text)); f.write("\n")

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

if __name__ == '__main__':

    os.makedirs("parsed", exist_ok=True)
    os.makedirs("raw", exist_ok=True)

    url = sys.argv[1]
    filename = url.split("/")[-1] + ".csv"

    with open("parsed/" + filename, "w", encoding="latin-1") as f:
        scrape_page(url, f)
