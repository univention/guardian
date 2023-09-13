import {defineStore} from 'pinia';
import type {SettingsConfig} from '@/stores/settings';
import type {AuthenticationPort} from '@/ports/authentication';
import type {DataPort} from '@/ports/data';
import {InMemoryAuthenticationAdapter, KeycloakAuthenticationAdapter} from '@/adapters/authentication';
import {InMemoryDataAdapter} from '@/adapters/data';
import {InvalidAdapterError} from '@/adapters/errors';

export const useAdapterStore = (config: SettingsConfig) => {
  return defineStore('adapter', () => {
    const authenticationAdapter: AuthenticationPort = (() => {
      const portSetting = config.authenticationPort.adapter;
      switch (portSetting) {
        case 'in_memory':
          return new InMemoryAuthenticationAdapter(
            config.authenticationPort.inMemoryConfig.username,
            config.authenticationPort.inMemoryConfig.isAuthenticated
          );
        case 'keycloak':
          return new KeycloakAuthenticationAdapter(
            config.authenticationPort.keycloakConfig.ssoUri,
            config.authenticationPort.keycloakConfig.realm,
            config.authenticationPort.keycloakConfig.clientId
          );
        default:
          throw new InvalidAdapterError(`Invalid authentication adapter: ${portSetting}`);
      }
    })();

    const dataAdapter: DataPort = (() => {
      const portSetting = config.dataPort.adapter;
      switch (portSetting) {
        case 'in_memory':
          return new InMemoryDataAdapter();
        default:
          throw new InvalidAdapterError(`Invalid data adapter: ${portSetting}`);
      }
    })();

    return {
      authenticationAdapter,
      dataAdapter,
    };
  })();
};
