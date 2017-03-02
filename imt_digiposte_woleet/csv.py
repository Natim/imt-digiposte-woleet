from __future__ import absolute_import

import csv


class CSVDialect(csv.Dialect):
    delimiter = ";"
    quotechar = None
    escapechar = None
    doublequote = None
    lineterminator = "\n"
    quoting = csv.QUOTE_NONE
    skipinitialspace = False
