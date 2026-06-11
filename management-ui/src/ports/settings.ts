/**
 * SPDX-License-Identifier: AGPL-3.0-only
 * SPDX-FileCopyrightText: 2026 Univention GmbH
 */

export const portSetting = 'managementUi.adapter.settingsPort';

export interface SettingsPort {
  // Load settings async
  init(): Promise<void>;

  // Get an app-related setting
  getSetting(settingName: string, defaultValue?: any): any;
}
