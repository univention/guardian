#!/bin/bash

# Copyright (C) 2024 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

poetry -C $PROJECT_DIR/management-api install
poetry -C $PROJECT_DIR/authorization-api install
poetry -C $PROJECT_DIR/guardian-lib install
yarn --cwd $PROJECT_DIR/management-ui install
