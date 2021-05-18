skywater-pdk related GitHub Actions
===================================

.. image:: https://img.shields.io/github/license/google/skywater-pdk-actions
   :alt: GitHub license - Apache 2.0
   :target: https://github.com/google/skywater-pdk-actions

.. image:: https://img.shields.io/github/v/tag/google/skywater-pdk-actions?include_prereleases&sort=semver
   :alt: Latest GitHub tag (including pre-releases)
   :target: https://gitHub.com/google/skywater-pdk-actions/commit/

.. image:: https://img.shields.io/github/commits-since/google/skywater-pdk-actions/v0.0
   :alt: GitHub commits since latest release (v0.0)
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

License
=======

The SkyWater Open Source PDK GitHub actions are released under the
`Apache 2.0 license <https://github.com/google/skywater-pdk/blob/master/LICENSE>`_.

The copyright details (which should also be found at the top of every file) are;

::

   Copyright 2021 SkyWater PDK Authors

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

