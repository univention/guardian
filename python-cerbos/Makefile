#!/usr/bin/make -f
#
# update python-cerbos src
#
# SPDX-FileCopyrightText: 2026 Univention GmbH
# SPDX-License-Identifier: AGPL-3.0-only

VERSION := 0.16.0
TAR_DIR := cerbos-sdk-python-$(VERSION)
TAR_FILE := cerbos-$(VERSION).tar.gz
TAR_URL := https://github.com/cerbos/cerbos-sdk-python/archive/refs/tags/v$(VERSION).tar.gz
SHA_FILE := $(TAR_FILE).sha256

.PHONY: all clean fetch unpack verify hash

all: unpack

fetch: $(TAR_FILE)

hash: $(SHA_FILE)

$(SHA_FILE): $(TAR_FILE)
	sha256sum $(TAR_FILE) > $(SHA_FILE)

$(TAR_FILE):
	wget -O $@ $(TAR_URL)

verify: $(TAR_FILE)
	sha256sum -c $(TAR_FILE).sha256

unpack: verify clean
	rm -rf $(TAR_DIR)
	tar xvzf $(TAR_FILE) \
		$(TAR_DIR)/src \
		$(TAR_DIR)/proto \
		$(TAR_DIR)/tests \
		$(TAR_DIR)/utils \
		$(TAR_DIR)/pdm.lock \
		$(TAR_DIR)/pyproject.toml
	mv $(TAR_DIR)/* .

clean:
	rm -rf $(TAR_DIR) src tests pyproject.toml pdm.lock proto utils
