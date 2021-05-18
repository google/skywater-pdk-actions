# Copyright 2021 SkyWater PDK Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

FROM ubuntu:20.04

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update
RUN apt-get install -y build-essential git curl python3 python3-pip tcl-dev tk-dev csh libcairo2-dev

WORKDIR /build

# Setup Magic
ENV MAGIC_TAG 8.3.160
RUN \
    curl -L https://github.com/RTimothyEdwards/magic/archive/refs/tags/${MAGIC_TAG}.tar.gz -o /build/magic.tar.gz \
    && sha256sum /build/magic.tar.gz \
    && mkdir /build/magic \
    && tar -xzC /build/magic --strip-components=1 -f /build/magic.tar.gz \
    && cd /build/magic \
    && ./configure \
    && make -j$(nproc) \
    && make install \
    && rm -rf /build/magic*

# Setup Python Dependencies
WORKDIR /build
COPY ./requirements.txt /build/requirements.txt
RUN \
	cat /build/requirements.txt \
	&& python3 -m pip install -r /build/requirements.txt --progress-bar off \
	&& rm -rf ~/.cache/pip

# OpenPDKs
## Tag must exist on both https://github.com/efabless/open_pdk_techfiles
## and https://github.com/RTimothyEdwards/open_pdks
ENV OPEN_PDKS_TAG 1.0.159

## Download run_standard_drc
RUN \
    curl -L https://raw.githubusercontent.com/RTimothyEdwards/open_pdks/${OPEN_PDKS_TAG}/sky130/custom/scripts/run_standard_drc.py -o /usr/bin/run_standard_drc.py \
    && sha256sum /usr/bin/run_standard_drc.py

## Download Precompiled OpenPDKs Magic Tech Files
ENV PDK_ROOT /share/pdk/sky130A
RUN \
    curl -L https://github.com/efabless/open_pdk_techfiles/releases/download/${OPEN_PDKS_TAG}/sky130A_tech_magic.tar.xz -o /build/sky130A_tech_magic.tar.xz \
    && sha256sum /build/sky130A_tech_magic.tar.xz \
    && mkdir -p ${PDK_ROOT}/libs.tech/magic \
    && tar -xC ${PDK_ROOT}/libs.tech/magic -f /build/sky130A_tech_magic.tar.xz \
    && rm -rf /build/*

# Copy Entry Point
COPY ./run_all_drc.py /usr/bin/run_all_drc.py
RUN chmod +x /usr/bin/run_all_drc.py

ENTRYPOINT ["/usr/bin/run_all_drc.py"]
