.. Astronet documentation master file, created by
   sphinx-quickstart on Fri Nov 30 14:55:25 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Astronet's documentation!
====================================

Contents:

.. toctree::
    :maxdepth: 2
   
    api
    tutorial


Account
-------

.. module:: astronet.account

.. autofunction:: login

.. autofunction:: logout

.. autofunction:: register

.. autofunction:: reset_pass

.. autofunction:: reset_pass_finalize

Main views
----------

.. module:: astronet

.. autofunction:: home

.. autofunction:: add_post

.. autofunction:: show_post


Helper functions
----------------

.. module:: astronet.helpers

.. autofunction:: login_required

.. autofunction:: send_base64

.. autofunction:: gen_filename

.. autofunction:: query_db

.. autofunction:: stringify

.. autofunction:: create_query

.. autofunction:: get_size

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

