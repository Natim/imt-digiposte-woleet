import argparse
import csv
import codecs
import os

from .files import files_lookup
from .digiposte import create_account, upload_diploma


DEFAULT_SCHEMA_FILE = 'students.csv'
DEFAULT_DIPLOMAS_DIR = 'diplomas/'
DEFAULT_ROUTAGE_FILE = 'routage.csv'
STUDENTS_FIELD_NAMES = ['ETAT_CIVIL', 'PRENOM_ELE', 'NOM_NAISSANCE', 'NUMERO', 'EMAIL_ELE']
ROUTAGE_FIELD_NAMES = ['NUMERO', 'ROUTAGE']
DIPLOMA_EXT = '.pdf'
RECEIPT_EXT = '.json'


def main(args=None):
    parser = argparse.ArgumentParser(
        description='Import the blocklists from the addons server into Kinto.')

    parser.add_argument('-s', '--student-file', help='CSV students file',
                        type=str, default=DEFAULT_SCHEMA_FILE)

    parser.add_argument('--no-students', help='Do not create students account.',
                        action="store_false")

    parser.add_argument('-r', '--routage-file',
                        help='Students digiposte account routage CSV file.',
                        type=str, default=DEFAULT_ROUTAGE_FILE)

    parser.add_argument('-d', '--diplomas-dir', help='Diploma directory.',
                        type=str, default=DEFAULT_DIPLOMAS_DIR)

    parser.add_argument('--no-upload', help='Do not upload diploma on digiposte.',
                        action="store_false")

    args = parser.parse_args(args=args)

    digiposte_bearer_token = os.getenv("DIGIPOSTE_BEARER_TOKEN")
    diplomas_dir = os.path.join(os.getcwd(), args.diplomas_dir)

    if not digiposte_bearer_token:
        raise ValueError('Please expose the DIGIPOSTE_BEARER_TOKEN env variable')

    routages = None

    if not args.no_students:
        routages = []
        with codecs.open(args.student_file, 'r', encoding='utf-8') as students_csv_file:
            students_reader = csv.DictReader(students_csv_file, STUDENTS_FIELD_NAMES)
            for student in students_reader:
                student_routage = create_account(
                    bearer_token=digiposte_bearer_token,
                    partner_user_id=student['NUMERO'],
                    first_name=student['PRENOM_ELE'],
                    last_name=student['NOM_NAISSANCE'])
                student["ROUTAGE"] = student_routage
                routages.append(student)

    if not routages:
        with codecs.open(args.routage_file, 'r', encoding='utf-8') as routage_csv_file:
            routages = list(csv.DictReader(routage_csv_file, ROUTAGE_FIELD_NAMES))

    if not args.no_upload:
        students_routages = {routage['NUMERO']: routage['ROUTAGE'] for routage in routages}
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
            upload_diploma(students_diplomas[numero],
                           students_routages[numero],
                           bearer_token=digiposte_bearer_token)
