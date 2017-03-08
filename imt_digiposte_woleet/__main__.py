from __future__ import absolute_import, print_function
import argparse
import csv
import codecs
import os
import requests

from .csv import CSVDialect
from .files import files_lookup
from .digiposte import create_account, upload_diploma, get_student_url

DIGIPOSTE_BASE_URL = "https://api.digiposte.fr/api/v3"  # No trailing slash

DEFAULT_SCHEMA_FILE = 'students.csv'
DEFAULT_DIPLOMAS_DIR = 'diplomas/'
DEFAULT_ROUTAGE_FILE = 'students-routage.csv'
DEFAULT_URL_FILE = 'students-urls.csv'
STUDENTS_FIELD_NAMES = ['ETAT_CIVIL', 'PRENOM_ELE', 'NOM_NAISSANCE',
                        'NUMERO', 'DIPLOME_OBTENU', 'EMAIL_ELE']
ROUTAGE_FIELD_NAMES = ['NUMERO', 'ROUTAGE', 'ETAT_CIVIL', 'PRENOM_ELE', 'NOM_NAISSANCE',
                       'DIPLOME_OBTENU', 'EMAIL_ELE']
DIPLOMA_EXT = '.pdf'
RECEIPT_EXT = '.json'


def main(args=None):
    parser = argparse.ArgumentParser(
        description='Import the blocklists from the addons server into Kinto.')

    parser.add_argument('-s', '--student-file', help='CSV students file',
                        type=str, default=DEFAULT_SCHEMA_FILE)

    parser.add_argument('--no-students', help='Do not create students account.',
                        action="store_true")

    parser.add_argument('-r', '--routage-file',
                        help='Students digiposte account routage CSV file.',
                        type=str, default=DEFAULT_ROUTAGE_FILE)

    parser.add_argument('-f', '--override',
                        help='Override the routage file if already exist.',
                        action="store_true")

    parser.add_argument('-d', '--diplomas-dir', help='Diploma directory.',
                        type=str, default=DEFAULT_DIPLOMAS_DIR)

    parser.add_argument('--no-upload', help='Do not upload diploma on digiposte.',
                        action="store_true")

    parser.add_argument('-u', '--url-file',
                        help='Students digiposte account url CSV file.',
                        type=str, default=DEFAULT_URL_FILE)

    parser.add_argument('--no-urls', help='Do not grab the student URL.',
                        action="store_true")

    args = parser.parse_args(args=args)

    digiposte_bearer_token = os.getenv("DIGIPOSTE_BEARER_TOKEN")
    diplomas_dir = os.path.join(os.getcwd(), args.diplomas_dir)

    if not digiposte_bearer_token:
        raise ValueError('Please expose the DIGIPOSTE_BEARER_TOKEN env variable')

    digiposte_session = requests.Session()
    digiposte_session.headers.update(
        {"Authorization": "Bearer {}".format(digiposte_bearer_token)})

    routages = []
    with codecs.open(args.student_file, 'r', encoding='utf-8') as students_csv_file:
        students_reader = csv.DictReader(students_csv_file,
                                         dialect=CSVDialect(),
                                         fieldnames=STUDENTS_FIELD_NAMES)
        next(students_reader)  # Ignore first line
        for student in students_reader:
            first_name = student['PRENOM_ELE'].split(',', 1)[0].strip()
            print("{} {} - {}".format(first_name,
                                      student['NOM_NAISSANCE'].upper(),
                                      student['NUMERO']), end=' : ')
            if not args.no_students:
                student_routage = create_account(digiposte_session, DIGIPOSTE_BASE_URL,
                                                 partner_user_id=student['NUMERO'],
                                                 first_name=first_name,
                                                 last_name=student['NOM_NAISSANCE'])
                if student_routage:
                    student["ROUTAGE"] = student_routage
                    routages.append(student)
                    print('OK - Routage {}'.format(student_routage))
                else:
                    print('NOK - Account already created')
            else:
                print('Creation skipped')

    if not routages:
        if not os.path.isfile(args.routage_file):
            raise ValueError('Please provide a routage_file: {} not found.'.format(
                args.routage_file))

        with codecs.open(args.routage_file, 'r', encoding='utf-8') as routage_csv_file:
            routage_reader = csv.DictReader(routage_csv_file,
                                            dialect=CSVDialect(),
                                            fieldnames=ROUTAGE_FIELD_NAMES)
            next(routage_reader)  # Ignore first line
            routages = list(routage_reader)
    else:
        if os.path.isfile(args.routage_file) and not args.override:
            raise ValueError('{} already exists. Please use -f if you want to override it.')
        with codecs.open(args.routage_file, 'w', encoding='utf-8') as routage_csv_file:
            writer = csv.DictWriter(routage_csv_file,
                                    dialect=CSVDialect(),
                                    fieldnames=ROUTAGE_FIELD_NAMES)
            writer.writeheader()
            for routage in routages:
                writer.writerow(routage)

    if not args.no_upload:
        students_routages = {routage['NUMERO']: routage['ROUTAGE'] for routage in routages}
        students_diploma_name = {routage['NUMERO']: routage['DIPLOME_OBTENU']
                                 for routage in routages}
        students_diplomas = files_lookup(diplomas_dir,
                                         diploma_ext=DIPLOMA_EXT,
                                         receipt_ext=RECEIPT_EXT)

        diplomas_numeros = set(students_diplomas.keys())
        routages_numeros = set(students_routages.keys())

        students_codes = diplomas_numeros & routages_numeros

        ignored_diplomas = diplomas_numeros - routages_numeros
        ignored_routages = routages_numeros - diplomas_numeros

        if ignored_diplomas:
            print('Ignoring diplomas because missing routage: {}'.format(ignored_diplomas))

        if ignored_routages:
            print('Ignoring routages because missing diplomas: {}'.format(ignored_routages))

        for numero in students_codes:
            upload_diploma(digiposte_session, DIGIPOSTE_BASE_URL,
                           diploma_name=students_diploma_name[numero],
                           diploma_info=students_diplomas[numero],
                           route_code=students_routages[numero])

    if not args.no_urls:
        students_numeros = {routage['NUMERO']: routage for routage in routages}

        urls = []
        for numero, student in students_numeros.items():
            customization_url = get_student_url(digiposte_session, DIGIPOSTE_BASE_URL, numero)
            if customization_url:
                student['CUSTOMIZATION_URL'] = customization_url
                urls.append(student)

        with codecs.open(args.url_file, 'w', encoding='utf-8') as customization_csv_file:
            writer = csv.DictWriter(customization_csv_file,
                                    dialect=CSVDialect(),
                                    fieldnames=ROUTAGE_FIELD_NAMES + ['CUSTOMIZATION_URL'])
            writer.writeheader()
            for student in urls:
                writer.writerow(student)
