import json
import os
from tqdm import tqdm
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTTextBoxHorizontal, LTRect
import pandas as pd

import matplotlib.pyplot as plt
from collections import defaultdict


def extract_table(pdf_path):
    # List to hold the extracted data
    words_data = []

    # Loop through each page of the PDF
    for i, page_layout in enumerate(extract_pages(pdf_path)):
        page_data_raw = []

        non_page_data = []
        max_x = 0
        max_y = 0
        min_x = 100000
        min_y = 100000
        # Extract text from text containers (blocks)
        for element in page_layout:
            if isinstance(element, LTTextBoxHorizontal):
                # text = element.get_text()
                page_data_raw.append(element)
            elif isinstance(element, LTRect):
                non_page_data.append(element)
                if element.x0 > max_x:
                    max_x = element.x0
                if element.y0 > max_y:
                    max_y = element.y0
                if element.x0 < min_x:
                    min_x = element.x0
                if element.y0 < min_y:
                    min_y = element.y0

                if element.x1 > max_x:
                    max_x = element.x1
                if element.y1 > max_y:
                    max_y = element.y1
                if element.x1 < min_x:
                    min_x = element.x1
                if element.y1 < min_y:
                    min_y = element.y1
        upper_left = (min_x, max_y)
        lower_right = (max_x, min_y)
        page_data = set()
        for element in page_data_raw:
            if element.y0 > upper_left[1] or element.y1 < lower_right[1]:
                pass
            else:
                for text_line in element:
                    page_data.add(text_line)
        page_data = list(page_data)

        # Sort page_data by x and y values
        page_data.sort(key=lambda x: (-x.y1, x.x0))
        non_page_data.sort(key=lambda x: (-x.y1, x.x0))

        for x in page_data:
            print(x)
        print()
        # for x in non_page_data:
        #     print(x)
        tl = sorted({x.x0 for x in non_page_data})
        boundaries = [(tl[i], tl[i + 2]) for i in range(0, len(tl) - 2, 2)]
        columns = defaultdict(list)
        last_x = 0
        for textbox in page_data:
            if textbox.x0 <= last_x and textbox.x0 >= boundaries[0][1]:
                for i, (left, right) in enumerate(boundaries):
                    if textbox.x0 >= left and textbox.x0 <= right:
                        if columns[i]:
                            last_str = columns[i].pop()
                        else:
                            last_str = ""
                        columns[i].append(
                            f"{last_str} {textbox.get_text().strip()}".strip()
                        )
                        # last_x = textbox.x0
            else:
                for i, (left, right) in enumerate(boundaries):
                    if textbox.x0 >= left and textbox.x0 <= right:
                        for text in textbox.get_text().strip().split("\n"):
                            if textbox.x1 >= right:
                                # find the character which croses the boundary
                                leftmost_crosser = ""
                                rightmost = ""
                                for char in textbox:
                                    if isinstance(char, LTChar):
                                        if char.x1 >= right:
                                            rightmost += char.get_text()
                                        else:
                                            leftmost_crosser += char.get_text()
                                # # figure out which leftmost_crosser is or rigghtmost is the number and which is the word
                                # if i == 2 and leftmost_crosser.strip().isnumeric():
                                #     columns[i+1].append(leftmost_crosser.strip())
                                #     columns[i].append(rightmost.strip())
                                # else:
                                leftmost_crosser = leftmost_crosser.strip()
                                rightmost = rightmost.strip()
                                # which column is numeric?
                                # if i == 2 and leftmost_crosser.isnumeric():
                                #     columns[i+1].append(leftmost_crosser)
                                #     columns[i].append(rightmost)
                                # else:
                                columns[i].append(leftmost_crosser)
                                columns[i + 1].append(rightmost)
                            else:
                                columns[i].append(text.strip())
                            last_x = textbox.x0
                            break
        dtypes = {"Frequency1": int, "Frequency2": int}
        try:
            # get columns into a df
            df = pd.DataFrame(columns)

        except:
            lens = list({len(x) for x in columns.values()})
            if len(lens) == 2:
                if abs(lens[0] - lens[1]) == 1:
                    columns[5].pop()
                    try:
                        df = pd.DataFrame(columns)

                    except:
                        print([len(columns[i]) for i in range(6)])
                        columns[5].append("1")
                        columns[5].append("")
                        columns[4].append("")
                        columns[3].append("")
                        print([len(columns[i]) for i in range(6)])
                        # df = pd.DataFrame(columns)

            else:
                print(lens)
                print([len(x) for x in columns.values()])
                print(columns[2])
                # for each value in columns[0], if it starts with a "/", then add it to the preceding entry and shorten the list
                for key in columns.keys():
                    for i in range(1, len(columns[key])):
                        if columns[key][i].startswith("/"):
                            columns[key][i - 1] += columns[key][i]
                            columns[key][i] = "DELETED-"
                    columns[key] = [x for x in columns[key] if x != "DELETED-"]
                print()
                min_len = min([len(x) for x in columns.values()])
                for key in columns.keys():
                    if len(columns[key]) == 1 + min_len:
                        columns[key][1] = f"{columns[key][0]} {columns[key][1]}"
                        del columns[key][0]
                print(lens)
                print([len(x) for x in columns.values()])
                print(columns[2])

                # breakpoint()
                # the first row is actualy the index
        try:
            df = pd.DataFrame(columns)
        except:
            print("badcolumns")
            print(lens)
            print([len(x) for x in columns.values()])
            print(columns[2])
            for key in columns.keys():
                for i in range(1, len(columns[key])):
                    # if columns[key][i] == '-':
                    #     columns[key][i] = "DELETED"
                    if " " in columns[key][i] and key in [0, 3]:
                        columns[key][i] = columns[key][i].replace(" ", "")
                columns[key] = [x for x in columns[key] if x != "DELETED-" and x]
            print("bettercolumns")
            print(lens)
            print([len(x) for x in columns.values()])
            print(columns[2])
            # breakpoint()
            try:
                df = pd.DataFrame(columns)
            except:
                for key in columns.keys():
                    for i in range(1, len(columns[key])):
                        if key == 0 and not columns[key][i - 1].endswith("-"):
                            columns[key][
                                i - 1
                            ] = f"{columns[key][i-1]}{columns[key][i]}"
                            columns[key][i] = "DELETED-"
                    columns[key] = [x for x in columns[key] if x != "DELETED-" and x]
                    try:
                        df = pd.DataFrame(columns)
                    except:
                        print("lastcolumns")
                        print([len(x) for x in columns.values()])
                        breakpoint()
        df.columns = [
            "Words1",
            "Meaning1",
            "Frequency1",
            "Words2",
            "Meaning2",
            "Frequency2",
        ]
        df = df.drop(0)
        # df["Frequency2"] = 1
        try:
            df = df.astype(dtypes)
        except:
            print("badnumbers")
            break
        # add df values to words_data
        words_data.append(df)

    # Combine all dataframes into a single dataframe
    words_df = pd.concat(words_data, ignore_index=True)
    # Now we need to split the df in the middle between the 3-3 columns, and stack the right column underneath the left column
    left_df = words_df.iloc[:, :3]
    right_df = words_df.iloc[:, 3:]
    # Add "pos" tag "verb" to the left_df and "noun" to the right_df
    left_df["pos"] = "verb"
    right_df["pos"] = "noun"
    # breakpoint()
    # set columns to same name
    right_df.columns = left_df.columns
    words_df = pd.concat([left_df, right_df], ignore_index=True)
    # Reset the index
    words_df.reset_index(drop=True, inplace=True)
    # delete the last row
    words_df = words_df[:-1]
    return words_df


# Update the path to your PDF file
pdf_path = "table_2.pdf"
word_df = extract_table(pdf_path)
# extract_definitions_by_color_and_size(pdf_path, target_color, min_font_size)

# Show histogram in matplotlib of the buckets of 25 from 600 to 0 from word_df["Frequency1"]
# filter out strings which cannot become ints
# breakpoint()
# word_df = word_df[word_df["Frequency1"].str.isnumeric()]
word_df["Frequency1"] = word_df["Frequency1"].astype(int)
# sort the dataframe by frequency descending
word_df = word_df.sort_values(by="Frequency1", ascending=False)
# Plot the histogram of the frequency values
# Calculate the cumulative sum of frequencies for the Pareto line
word_df["Cumulative"] = word_df["Frequency1"].cumsum()

# Create the Pareto chart
# fig, ax1 = plt.subplots(figsize=(10, 6))

# # Plot the bar chart for the frequencies
# ax1.bar(word_df['Words1'], word_df['Frequency1'], color='blue', alpha=0.7, label='Frequency', width=0.4)
# ax1.set_xlabel('Words')
# ax1.set_ylabel('Frequency', color='blue')
# ax1.tick_params(axis='y', labelcolor='blue')

# # Plot the cumulative line chart for the Pareto line
# ax2 = ax1.twinx()
# ax2.plot(word_df['Words1'], word_df['Cumulative'], color='red', marker='o', label='Cumulative Frequency')
# ax2.set_ylabel('Cumulative Frequency', color='red')
# ax2.tick_params(axis='y', labelcolor='red')

# # Title and grid
# plt.title('Pareto Chart of Word Frequencies')
# fig.tight_layout()
# plt.grid(True)
# plt.show()

# Get df where frequency is greater than 7
word_df_most = word_df.iloc[:200]

from fuzzywuzzy import fuzz


def fuzzy_best_match(word, dat, top_n=1):
    scores = [(i, fuzz.ratio(word, x["headword"])) for (i, x) in enumerate(dat)]
    scores.sort(key=lambda x: x[1], reverse=True)
    return [dat[i[0]] for i in scores[:top_n]]


with open(
    os.path.join(os.path.dirname(__file__), "dict_w_conjugations.json"),
    "r",
    encoding="utf-8",
) as f:
    mvskoke_dict = json.load(f)

word_df_most["headword"] = word_df_most["Words1"].apply(
    lambda x: x.split("/")[0].replace("-", "etv").strip()
)
most_verbs = word_df_most[word_df_most["pos"] == "verb"]

# for each verb in most_verbs, find the best match in mvskoke_dict with fuzzy_best_match
most_verbs["best_match"] = most_verbs["headword"].apply(
    lambda x: fuzzy_best_match(x, mvskoke_dict, 1)
)

# save as quiz easymode.json
with open("quiz_easymode.json", "w", encoding="utf-8") as f:
    # just save the best_match
    json.dump(most_verbs["best_match"].tolist(), f, ensure_ascii=False, indent=4)
