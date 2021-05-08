``skywater-pdk-actions`` - ``modules-magic-drc``
====================================================

This GitHub action runs Design Rule Checks on all GDS files inside the /cells directory.

Written by `Donn <https://github.com/donn>`_ in collaboration with `Tim Edwards <https://github.com/rtimothyedwards>`_.

Usage:
======

Add this to any push, PR or manual dispatch workflow:

.. code:: yml

       steps:
         - uses: actions/checkout@v2
         - name: Run Magic DRC
           uses: google/skywater-pdk-actions/modules-magic-drc@main

Check action.yml for optional arguments.

.. include:: ../docs/contributing.rst

.. include:: ../docs/license.rst
