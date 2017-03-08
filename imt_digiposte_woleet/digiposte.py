# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from requests.exceptions import HTTPError
from time import sleep
import hashlib
import os.path

DIGIPOSTE_DIPLOMA_TITLE = "Diplôme {} - IMT Atlantique-TB - 2017"
DIGIPOSTE_DIPLOMA_TYPE = "DIPLOME"

DIGIPOSTE_RECEIPT_TITLE = "Woleet receipt"
DIGIPOSTE_RECEIPT_TYPE = "RECU_ANCRAGE"

DIPLOMA_FILENAME_PREFIX = "diplome_doctorat_"
RECEIPT_FILENAME_PREFIX = "recu_diplome_doctorat_"
FILE_HASH_ALGORITHM = "SHA256"


def create_account(session, base_url, partner_user_id, first_name, last_name):
    body = {
        "partner_user_id": partner_user_id,
    }

    if first_name:
        body['first_name'] = first_name
    if last_name:
        body['last_name'] = last_name

    response = session.post("{}/user/partial".format(base_url), json=body)
    if response.status_code == 409:
        headers = {'X-PartnerUserId': partner_user_id}
        response = session.get("{}/memberships".format(base_url), headers=headers)
        response.raise_for_status()
        body = response.json()
        return body['memberships'][0]['id']
    else:
        body = response.json()
        try:
            response.raise_for_status()
        except HTTPError:
            if response.status_code == 400:
                if 'firstName' in body:
                    return create_account(session, base_url, partner_user_id, None, last_name)
                if 'lastName' in body:
                    return create_account(session, base_url, partner_user_id, first_name, None)
            print("\nHTTPError {} for {}.\n{}".format(
                  response.status_code,
                  partner_user_id, body))
            return None
    return body['route_code']


def upload_diploma(session, base_url, diploma_info, route_code, diploma_name):
    # Upload diploma
    headers = {"X-API-VERSION-MINOR": "2",
               "X-RouteCode": route_code}

    with open(diploma_info['diploma'], 'rb') as diploma:
        content = diploma.read()
        file_hash = hashlib.sha256(content).hexdigest()
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
        file_hash = hashlib.sha256(content).hexdigest()
        file_size_bytes = len(content)

        receipt.seek(0)  # Rewind file for upload

        receipt_data = {
            "title": DIGIPOSTE_RECEIPT_TITLE + " - " + title_diploma,
            "type": DIGIPOSTE_RECEIPT_TYPE,
            "file_name": "{}{}".format(RECEIPT_FILENAME_PREFIX,
                                       os.path.basename(diploma_info['diploma'])),
            "hash": file_hash,
            "algo": FILE_HASH_ALGORITHM,
            "file_size": file_size_bytes
        }
        print("Uploading receipt: {}".format(receipt_data))
        response = session.post('{}/document/certified'.format(base_url),
                                data=receipt_data, files={"archive": receipt},
                                headers=headers)
        response.raise_for_status()
    print('---')


def get_student_url(session, base_url, partner_user_id):
    headers = {"X-PartnerUserId": partner_user_id,
               "Content-Type": "application/json"}

    response = session.post("{}/user/customizationurl".format(base_url), headers=headers)
    if response.status_code == 403:
        print('This student ({}) has already consumed her customization '
              'url and created an account.'.format(partner_user_id))
        return None
    response.raise_for_status()

    body = response.json()
    return body.get('customization_url')
