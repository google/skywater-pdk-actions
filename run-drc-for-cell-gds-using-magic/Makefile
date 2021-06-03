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

TOP_DIR := $(realpath $(dir $(lastword $(MAKEFILE_LIST)))/..)

NAME := run-drc-for-cell-gds-using-magic

tests/action-local/action.yml: action.yml .update-test-action-local.py
	$(TOP_DIR)/$(NAME)/.update-test-action-local.py

.PHONY: tests/action-local/action.yml

README.rst: README.src.rst $(TOP_DIR)/docs/*.rst $(TOP_DIR)/Makefile
	make -C $(TOP_DIR) $(NAME)/README.rst

# Redirect everything to the top directory by default.
%:
	make -C $(TOP_DIR) $@
