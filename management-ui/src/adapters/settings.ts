import type {SettingsPort} from '@/ports/settings';

const getSettingString = (settingAlias: string): string => {
  const base = settingAlias
    .replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`)
    .replace(/\./g, '__')
    .toUpperCase();
  return `VITE__${base}`;
};

export class EnvSettingsAdapter implements SettingsPort {
  private _settings: Map<string, string>;

  constructor() {
    this._settings = new Map<string, string>();
  }

  async init(): Promise<void> {
    return;
  }

  getSetting(settingName: string, defaultValue?: any): any {
    if (!this._settings.has(settingName)) {
      this._settings.set(settingName, import.meta.env[getSettingString(settingName)]);
    }
    return this._settings.get(settingName) ?? defaultValue;
  }
}

export class UrlSettingsAdapter implements SettingsPort {
  private readonly _configUrl: string;
  private readonly _useProxy: boolean;
  private _settings: Map<string, string>;

  constructor(configUrl?: string, useProxy: boolean = false) {
    this._settings = new Map<string, any>();

    let url = configUrl ?? '';
    if (configUrl === '') {
      const defaultUrl = import.meta.env.BASE_URL.replace(/\/$/, '');
      url = `${defaultUrl}/config.json`;
    } else if (useProxy) {
      const baseUrl = new URL(url);
      url = baseUrl.pathname;
    }
    this._useProxy = useProxy;
    this._configUrl = url;
  }

  async init(): Promise<void> {
    const settingsResponse = await fetch(this._configUrl);
    if (settingsResponse.ok) {
      const settings = (await settingsResponse.json()) as Record<string, string>;
      Object.keys(settings).forEach(key => {
        this._settings.set(key, settings[key]);
      });
    } else {
      throw new Error(`SettingsPort: Unable to fetch ${this._configUrl}`);
    }
  }

  getSetting(settingName: string, defaultValue?: any): any {
    return this._settings.get(getSettingString(settingName)) ?? defaultValue;
  }
}
