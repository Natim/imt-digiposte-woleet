Delivering Diploma in Digiposte while anchoring them in the blockchain
======================================================================

Create students accounts at digiposte and upload their diploma and woleet receipt there.

Install and run
---------------

First of all get an Oauth Bearer Token from Digiposte.

Get your ``client_id`` and ``client_secret`` from Digiposte.

::
   
   http -f POST https://api.u-post.fr/oauth/token grant_type=client_credentials \
       --auth client_id:client_secret
   {"token_type":"bearer","access_token":"AAAAAAA...AAAAAAAAA"}

::

    DIGIPOSTE_BEARER_TOKEN="AAAAAAA...AAAAAAAAA" \
	    load_students --students-file students.csv --diploma-dir diplomas/


Script parameters
-----------------

- ``--students-file`` parameter is a UTF-8 encoded CSV file with column separated by ``;``.
- ``--diploma-dir`` parameter is a directory containing PDF files as ``NUMERO_ELEVE.pdf``
  and Chainpoint receipts as ``NUMERO_ELEVE.json``


More Information
----------------

* **Python**: 2.7+
* Delivery is done using `Digiposte <https://secure.digiposte.fr/>`_
* Anchoring is done using `Woleet <https://woleet.io/>`_ API.
