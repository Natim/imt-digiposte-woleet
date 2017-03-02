# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import hashlib
import os.path

DIGIPOSTE_DIPLOMA_TITLE = "Diplôme {} - IMT Atlantique-TB - 2017"
DIGIPOSTE_DIPLOMA_TYPE = "DIPLOME"

DIGIPOSTE_RECEIPT_TITLE = "Woleet receipt"
DIGIPOSTE_RECEIPT_TYPE = "RECEIPT"

DIPLOMA_FILENAME_PREFIX = "diplome_doctorat_"
RECEIPT_FILENAME_PREFIX = "recu_diplome_doctorat_"
FILE_HASH_ALGORITHM = "SHA1"


def create_account(session, base_url, partner_user_id, first_name, last_name):
    response = session.post("{}/user/partial".format(base_url), json={
        "partner_user_id": partner_user_id,
        "first_name": first_name,
        "last_name": last_name
    })
    if response.status == 409:
        print("The account has already been created ({}). "
              "If you don't have the route_code you are screwed.".format(partner_user_id))
    else:
        response.raise_for_status()
    body = response.json()
    return body['route_code']


def upload_diploma(session, base_url, diploma_info, route_code, diploma_name):
    # Upload diploma
    headers = {"X-API-VERSION-MINOR": "2",
               "X-RouteCode": route_code}

    with open(diploma_info['diploma'], 'rb') as diploma:
        content = diploma.read()
        file_hash = hashlib.sha1(content).hexdigest()
        file_size_bytes = len(content)

        diploma.seek(0)  # Rewind file for upload

        title_diploma = DIGIPOSTE_DIPLOMA_TITLE.format(diploma_name)
        diploma_data = {
            "title": title_diploma,
            "type": DIGIPOSTE_DIPLOMA_TYPE,
            "file_name": "{}{}".format(DIPLOMA_FILENAME_PREFIX,
                                       os.path.basename(diploma_info['diploma'])),
            "hash": file_hash,
            "algo": FILE_HASH_ALGORITHM,
            "file_size": file_size_bytes
        }
        print("Uploading diploma: {}".format(diploma_data))
        response = session.post('{}/document/certified'.format(base_url),
                                data=diploma_data, files={"archive": diploma},
                                headers=headers)
        response.raise_for_status()

    # Upload receipt
    with open(diploma_info['receipt'], 'rb') as receipt:
        content = receipt.read()
        file_hash = hashlib.sha1(content).hexdigest()
        file_size_bytes = len(content)

        receipt.seek(0)  # Rewind file for upload

        receipt_data = {
            "title": DIGIPOSTE_RECEIPT_TITLE + title_diploma,
            "type": DIGIPOSTE_RECEIPT_TYPE,
            "file_name": "{}{}".format(RECEIPT_FILENAME_PREFIX,
                                       os.path.basename(diploma_info['diploma'])),
            "hash": file_hash,
            "algo": FILE_HASH_ALGORITHM,
            "file_size": file_size_bytes
        }
        print("Uploading receipt: {}".format(diploma_data))
        response = session.post('{}/document/certified'.format(base_url),
                                data=receipt_data, files={"archive": receipt},
                                headers=headers)
        response.raise_for_status()
    print('---')
