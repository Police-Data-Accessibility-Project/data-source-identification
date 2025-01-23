import ast
import csv
import os
import sys

""" This script cleans up raw website data from the tag collector 
    so that it may be used for effective training.
    It primarily merges list of strings into a single string, 
    removing brackets and quotes from the string.
"""


csv.field_size_limit(sys.maxsize)
FILE = "clean-data-example.csv"

with open(FILE, newline="") as readFile, open("new.csv", "w", newline="") as writeFile:
    reader = csv.DictReader(readFile)
    fieldnames = [
        "url",
        "url_path",
        "label",
        "html_title",
        "meta_description",
        "root_page_title",
        "http_response",
        "keywords",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "div_text",
    ]
    writer = csv.DictWriter(writeFile, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        write_row = row

        for key, value in write_row.items():
            try:
                val_list = ast.literal_eval(value)
            except (SyntaxError, ValueError):
                continue

            # if key == "keywords":
            #    l = l[0:2]

            try:
                value = " ".join(val_list)
            except TypeError:
                continue

            write_row.update({key: value})

        writer.writerow(write_row)

    os.rename("new.csv", FILE)
