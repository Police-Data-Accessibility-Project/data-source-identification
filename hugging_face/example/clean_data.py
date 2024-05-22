import csv
import random
import sys


""" This script randomly seperates a csv into a train and test split for use in training.
    The script will filter out rows containing multiple labels and preservve at least one unique label for the test script.
"""


labels = set()
csv.field_size_limit(sys.maxsize)

with open("labeled-urls-headers_all.csv", newline="") as csvfile:
    reader = csv.DictReader(csvfile)
    # result = sorted(reader, key=lambda d: int(d["id"]))
    with open("train-urls.csv", "w", newline="") as writefile:
        writer = csv.writer(writefile)
        writer.writerow(["url", "label"])

        vd_writer = csv.writer(open("test-urls.csv", "w", newline=""))
        vd_writer.writerow(["url", "label"])

        for row in reader:
            label = row["label"]

            if "#" in label:
                continue

            url = row["url"]

            if not url:
                continue

            rand = random.randint(1, 13)

            if label not in labels:
                labels.add(label)
                writer.writerow([url, row["label"]])
            elif rand != 1:
                writer.writerow([url, row["label"]])
            else:
                vd_writer.writerow([url, row["label"]])
