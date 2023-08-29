import {defineStore} from 'pinia';
import type {SettingsConfig} from '@/stores/settings';
import type {AuthenticationPort} from '@/ports/authentication';
import {InMemoryAuthenticationAdapter} from '@/adapters/authentication';
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
        default:
          throw new InvalidAdapterError(`Invalid authentication adapter: ${portSetting}`);
      }
    })();

    return {
      authenticationAdapter,
    };
  })();
};
