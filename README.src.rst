skywater-pdk related GitHub Actions
===================================

.. image:: https://img.shields.io/github/license/google/skywater-pdk-actions
   :alt: GitHub license - Apache 2.0
   :target: https://github.com/google/skywater-pdk-actions

.. image:: https://img.shields.io/github/v/tag/google/skywater-pdk-actions?include_prereleases&sort=semver
   :alt: Latest GitHub tag (including pre-releases)
   :target: https://gitHub.com/google/skywater-pdk-actions/commit/

.. image:: https://img.shields.io/github/commits-since/google/skywater-pdk-actions/|TAG_VERSION|
   :alt: GitHub commits since latest release (|TAG_VERSION|)
   :target: https://gitHub.com/google/skywater-pdk-actions/commit/

This repository contains the GitHub actions uses with the
`Google skywater-pdk <https://github.com/google/skywater-pdk>`__ and
`related modules <https://github.com/google?q=skywater-pdk&type=&language=>`__.

.. image:: https://github.com/google/skywater-pdk/raw/master/docs/_static/skywater-pdk-logo.png
   :alt: Google + SkyWater Logo Image
   :align: center
   :target: https://github.com/google/skywater-pdk
   :width: 80%

Actions
=======

Modules Related
---------------

```modules-pr-backporter`` <./modules-pr-backporter>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``modules-pr-backporter`` action is used on the
`SkyWater modules <https://github.com/google?q=skywater-pdk-libs>`__
(such as the
`standard cells <https://github.com/google?q=skywater-pdk-libs-sky130_fd_sc>`__)
to enable automatic backporting of pull requests to older released
versions.

```modules-roller`` <./modules-roller>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``modules-roller`` action is used by
`the primary SkyWater PDK repo <https://github.com/google/skywater-pdk>`__
to automatically generate pull requests which update the GitHub submodules when
new changes are added to them.

CI Related
----------

-  TODO

Resources
=========

The latest SkyWater SKY130 PDK design resources can be viewed at the following locations:

* `On Github @ google/skywater-pdk <https://github.com/google/skywater-pdk>`_
* `Google CodeSearch interface @ https://cs.opensource.google/skywater-pdk <https://cs.opensource.google/skywater-pdk>`_
* `foss-eda-tools.googlesource.com/skywater-pdk <https://foss-eda-tools.googlesource.com/skywater-pdk/>`_


.. include:: docs/license.rst
