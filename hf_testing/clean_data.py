import csv
import random

with open("labeled_231207.csv", newline="") as csvfile:
    reader = csv.DictReader(csvfile)
    result = sorted(reader, key=lambda d: int(d["id"]))
    with open("train-urls.csv", "w", newline="") as writefile:
        writer = csv.writer(writefile)
        writer.writerow(["url", "label"])

        vd_writer = csv.writer(open("test-urls.csv", "w", newline=""))
        vd_writer.writerow(["url", "label"])

        for row in result:
            if "#" in row["label"]:
                continue

            url = row["text"].split(" ,")[0]

            rand = random.randint(1, 13)

            if rand != 1:
                writer.writerow([url, row["label"]])
            else:
                vd_writer.writerow([url, row["label"]])
