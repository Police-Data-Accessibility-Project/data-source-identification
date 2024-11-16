# import subprocess
# import os

record_types = [
    "accident reports",
    "arrest records",
    "calls for service",
    "car gps",
    "citations",
    "dispatch logs",
    "dispatch recordings",
    "field contacts",
    "incident reports",
    "misc police activity",
    "officer involved shootings",
    "stops",
    "surveys",
    "use of force reports",
    "vehicle pursuits",
    "complaints and misconduct",
    "daily activity logs",
    "training and hiring info",
    "personnel records",
    "annual and monthly reports",
    "budgets and finances",
    "contact info and agency meta",
    "geographic",
    "list of data sources",
    "policies and contracts",
    "crime maps and reports",
    "crime statistics",
    "media bulletins",
    "records request info",
    "resources",
    "sex offender registry",
    "wanted persons",
    "booking reports",
    "court cases",
    "incarceration records",
]

print(len(record_types))
# json_files = []


# for record_type in record_types:
#     json_file = record_type.replace(' ', '_') + '.json'
#     json_files.append(json_file)

# for json_file in json_files:
#     command = ['python', 'generate_detailed_muckrock_csv.py',
#                '--json_file', json_file]

#     try:
#         subprocess.run(command, check=True)
#     except subprocess.CalledProcessError as e:
#         print(f'An error occurred while processing "{json_file}": {e}')
