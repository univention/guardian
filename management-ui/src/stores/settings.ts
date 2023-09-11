import {defineStore} from 'pinia';
import {ref, type Ref} from 'vue';
import {authenticationPortSetting} from '@/ports/authentication';
import {dataPortSetting} from '@/ports/data';
import {inMemoryAuthenticationSettings, keycloakAuthenticationSettings} from '@/adapters/authentication';
import {inMemoryDataSettings} from '@/adapters/data';
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

interface KeycloakAuthenticationConfig {
  ssoUri: string;
  realm: string;
  clientId: string;
}

interface AuthenticationPortConfig {
  adapter: string;
  inMemoryConfig: InMemoryAuthenticationConfig;
  keycloakConfig: KeycloakAuthenticationConfig;
}

interface DataPortConfig {
  adapter: string;
}

export interface SettingsConfig {
  settingsPort: SettingsPortConfig;
  authenticationPort: AuthenticationPortConfig;
  dataPort: DataPortConfig;
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
      keycloakConfig: {
        ssoUri: '',
        realm: '',
        clientId: '',
      },
    },
    dataPort: {
      adapter: '',
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
    // InMemory Authentication Adapter settings
    config.value.authenticationPort.inMemoryConfig.isAuthenticated =
      settingsAdapter.getSetting(inMemoryAuthenticationSettings.isAuthenticated) !== '0';
    config.value.authenticationPort.inMemoryConfig.username = settingsAdapter.getSetting(
      inMemoryAuthenticationSettings.username,
      ''
    );
    // Keycloak AuthenticationAdapter settings
    config.value.authenticationPort.keycloakConfig.ssoUri = settingsAdapter.getSetting(
      keycloakAuthenticationSettings.ssoUri
    );
    config.value.authenticationPort.keycloakConfig.realm = settingsAdapter.getSetting(
      keycloakAuthenticationSettings.realm
    );
    config.value.authenticationPort.keycloakConfig.clientId = settingsAdapter.getSetting(
      keycloakAuthenticationSettings.clientId
    );

    // DataPortSettings
    config.value.dataPort.adapter = settingsAdapter.getSetting(dataPortSetting, '');

    initialized.value = true;
  };

  return {
    config,
    init,
  };
});
