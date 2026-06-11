/**
 * SPDX-License-Identifier: AGPL-3.0-only
 * SPDX-FileCopyrightText: 2026 Univention GmbH
 */

export class InvalidAdapterError extends Error {
  constructor(msg: string) {
    super(msg);
    Object.setPrototypeOf(this, InvalidAdapterError.prototype);
  }
}
