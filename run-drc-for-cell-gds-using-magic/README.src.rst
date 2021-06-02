``skywater-pdk-actions`` - ``run-drc-for-cell-gds-using-magic``
===============================================================

This GitHub action runs Design Rule Checks on all GDS files inside the /cells
directory.

Usage
-----

The GitHub Action is deployed in docker containers at;
 * `docker://gcr.io/skywater-pdk/actions/run-drc-for-cell-gds-using-magic <https://gcr.io/skywater-pdk/actions/run-drc-for-cell-gds-using-magic>`_
 * `docker://docker.pkg.github.com/google/skywater-pdk-actions/run-drc-for-cell-gds-using-magic <https://github.com/google/skywater-pdk-actions/packages/805235>`_

Add this to any push, PR or manual dispatch workflow:

.. code:: yml

       steps:
       - uses: actions/checkout@v2

       - name: Run DRC for cell GDS (using Magic)
         uses: docker://gcr.io/skywater-pdk/actions/run-drc-for-cell-gds-using-magic:latest
         with:
           args: --acceptable-errors-file /dev/null --match-directories . --known-bad ''

Check the Python file for more documentation on arguments.

.. include:: ../docs/contributing.rst

.. include:: ../docs/license.rst
