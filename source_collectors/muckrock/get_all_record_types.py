import subprocess

record_types = ['accident reports', 'arrest records', 'calls for service', 'car gps', 'citations', 'dispatch logs', 'dispatch recordings',
                'field contacts', 'incident reports', 'misc police activity', 'officer involved shootings', 'stops', 'surveys', 'use of force reports',
                'vehicle pursuits', 'complaints and misconduct', 'daily activity logs', 'training and hiring info', 'personnel records', 'annual and monthly reports',
                'budgets and finances', 'contact info and agency meta', 'geographic', 'list of data sources', 'policies and contracts', 'crime maps and reports',
                'crime statistics', 'media bulletins', 'records request info', 'resources', 'sex offender registry', 'wanted persons', 'booking reports',
                'court cases', 'incarceration records']

for record_type in record_types:
    command = ['python', 'search_foia_data_db.py', '--search_for', record_type]

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f'An error occurred while executing the command for "{
              record_type}": {e}')
