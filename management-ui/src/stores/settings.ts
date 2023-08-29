import {defineStore} from 'pinia';
import {ref, type Ref} from 'vue';
import {authenticationPortSetting} from '@/ports/authentication';
import {inMemoryAuthenticationSettings} from '@/adapters/authentication';
import type {SettingsPort} from '@/ports/settings';
import {EnvSettingsAdapter} from '@/adapters/settings';
import {InvalidAdapterError} from '@/adapters/errors';

interface SettingsPortConfig {
  adapter: string;
}

interface InMemoryAuthenticationConfig {
  isAuthenticated: boolean;
  username: string;
}

interface AuthenticationPortConfig {
  adapter: string;
  inMemoryConfig: InMemoryAuthenticationConfig;
}

export interface SettingsConfig {
  settingsPort: SettingsPortConfig;
  authenticationPort: AuthenticationPortConfig;
}

export const useSettingsStore = defineStore('settings', () => {
  const initialized = ref(false);

  const config: Ref<SettingsConfig> = ref({
    settingsPort: {
      adapter: '',
    },
    authenticationPort: {
      adapter: '',
      inMemoryConfig: {
        isAuthenticated: false,
        username: '',
      },
    },
  });

  const init = async (
    adapterName: string = import.meta.env.VITE__MANAGEMENT_UI__ADAPTER__SETTINGS_PORT,
    forceReinitialize = false
  ): Promise<void> => {
    // Don't take the time to hot-reload, unless we really mean it
    if (initialized.value && !forceReinitialize) {
      return;
    }

    config.value.settingsPort.adapter = adapterName;
    const settingsAdapter = ((): SettingsPort => {
      switch (adapterName) {
        case 'env':
          return new EnvSettingsAdapter();
        default:
          throw new InvalidAdapterError(`Invalid settings adapter: ${adapterName}`);
      }
    })();
    await settingsAdapter.init();

    // AuthenticationPort settings
    config.value.authenticationPort.adapter = settingsAdapter.getSetting(authenticationPortSetting, '');
    config.value.authenticationPort.inMemoryConfig.isAuthenticated =
      settingsAdapter.getSetting(inMemoryAuthenticationSettings.isAuthenticated) !== '0';
    config.value.authenticationPort.inMemoryConfig.username = settingsAdapter.getSetting(
      inMemoryAuthenticationSettings.username,
      ''
    );

    initialized.value = true;
  };

  return {
    config,
    init,
  };
});
