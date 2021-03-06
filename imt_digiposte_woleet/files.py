from glob import iglob
import os.path
from collections import defaultdict


def files_lookup(diplomas_dir, diploma_ext='.pdf', receipt_ext='.json'):
    if not os.path.isdir(diplomas_dir):
        raise ValueError('{} is not a directory'.format(diplomas_dir))

    pdf_numeros = set()
    receipts_numeros = set()
    files = defaultdict(dict)

    for filename in iglob(os.path.join(diplomas_dir, "*{}".format(diploma_ext))):
        numero = os.path.basename(filename).replace(diploma_ext, '')
        numero = numero.split('-', 1)[0]
        if numero.isdigit():
            pdf_numeros.add(numero)
            files[numero]['diploma'] = filename

    for filename in iglob(os.path.join(diplomas_dir, "*{}".format(receipt_ext))):
        numero = os.path.basename(filename).replace(receipt_ext, '')
        numero = numero.split('-', 1)[0]
        if numero.isdigit():
            receipts_numeros.add(numero)
            files[numero]['receipt'] = filename

    missing_receipts = pdf_numeros - receipts_numeros

    if missing_receipts:
        print("Missing receipts for diplomas: {}".format(missing_receipts))

    missing_diplomas = receipts_numeros - pdf_numeros
    if missing_diplomas:
        print("Missing diplomas for receipts: {}".format(missing_diplomas))

    if missing_receipts or missing_diplomas:
        raise ValueError('Some files are missing for the upload')

    return files
