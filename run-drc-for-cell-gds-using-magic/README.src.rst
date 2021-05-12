``skywater-pdk-actions`` - ``run-drc-for-cell-gds-using-magic``
=============================================================

This GitHub action runs Design Rule Checks on all GDS files inside the /cells
directory.

Usage
=====

Add this to any push, PR or manual dispatch workflow:

.. code:: yml

       steps:
       - uses: actions/checkout@v2

       - name: Run Magic DRC
         uses: docker://ghcr.io/google/skywater-pdk-actions-run-drc-for-cell-gds-using-magic:latest
         with:
           args: --acceptable-errors-file /dev/null --match-directories . --known-bad ''

Check the Python file for more documentation on arguments.

.. include:: ../docs/contributing.rst

.. include:: ../docs/license.rst
