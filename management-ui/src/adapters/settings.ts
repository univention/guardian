import type {SettingsPort} from '@/ports/settings';

export class EnvSettingsAdapter implements SettingsPort {
  private _settings: Map<string, any>;

  private _getSettingString(settingAlias: string): string {
    const base = settingAlias
      .replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`)
      .replace(/\./g, '__')
      .toUpperCase();
    return `VITE__${base}`;
  }

  constructor() {
    this._settings = new Map<string, any>();
  }

  async init(): Promise<void> {
    return;
  }

  getSetting(settingName: string, defaultValue?: any): any {
    if (!this._settings.has(settingName)) {
      this._settings.set(settingName, import.meta.env[this._getSettingString(settingName)]);
    }
    return this._settings.get(settingName) ?? defaultValue;
  }
}
