import {defineStore} from 'pinia';
import type {SettingsConfig} from '@/stores/settings';
import type {AuthenticationPort} from '@/ports/authentication';
import type {DataPort} from '@/ports/data';
import {InMemoryAuthenticationAdapter, KeycloakAuthenticationAdapter} from '@/adapters/authentication';
import {ApiDataAdapter, InMemoryDataAdapter} from '@/adapters/data';
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
        case 'test':
          return new InMemoryDataAdapter({
            apps: [
              {
                name: 'app-1',
                display_name: 'App 1',
                resource_url: 'https://localhost/guardian/management/apps/app-1',
              },
              {
                name: 'app-2',
                display_name: 'App 2',
                resource_url: 'https://localhost/guardian/management/apps/app-2',
              },
            ],
            capabilities: [],
            conditions: [],
            contexts: [],
            namespaces: [
              {
                name: `namespace-1`,
                display_name: `Namespace 1 for App 1`,
                resource_url: `https://localhost/guardian/management/namespaces/app-1/namespace-1`,
                app_name: `app-1`,
              },
              {
                name: `namespace-2`,
                display_name: `Namespace 2 for App 1`,
                resource_url: `https://localhost/guardian/management/namespaces/app-1/namespace-2`,
                app_name: `app-1`,
              },
              {
                name: `namespace-1`,
                display_name: `Namespace 1 for App 2`,
                resource_url: `https://localhost/guardian/management/namespaces/app-2/namespace-1`,
                app_name: `app-2`,
              },
              {
                name: `namespace-2`,
                display_name: `Namespace 2 for App 2`,
                resource_url: `https://localhost/guardian/management/namespaces/app-2/namespace-2`,
                app_name: `app-2`,
              },
            ],
            permissions: [],
            roles: [
              {
                name: 'role-1',
                display_name: 'Role 1 for App 1, Namespace 1',
                resource_url: 'https://localhost/guardian/management/roles/app-1/namespace-1/role-1',
                app_name: 'app-1',
                namespace_name: 'namespace-1',
              },
              {
                name: 'role-2',
                display_name: 'Role 2 for App 1, Namespace 1',
                resource_url: 'https://localhost/guardian/management/roles/app-1/namespace-1/role-2',
                app_name: 'app-1',
                namespace_name: 'namespace-1',
              },
              {
                name: 'role-1',
                display_name: 'Role 1 for App 1, Namespace 2',
                resource_url: 'https://localhost/guardian/management/roles/app-1/namespace-2/role-1',
                app_name: 'app-1',
                namespace_name: 'namespace-2',
              },
              {
                name: 'role-2',
                display_name: 'Role 2 for App 1, Namespace 2',
                resource_url: 'https://localhost/guardian/management/roles/app-1/namespace-2/role-2',
                app_name: 'app-1',
                namespace_name: 'namespace-2',
              },
              {
                name: 'role-1',
                display_name: 'Role 1 for App 2, Namespace 1',
                resource_url: 'https://localhost/guardian/management/roles/app-2/namespace-1/role-1',
                app_name: 'app-2',
                namespace_name: 'namespace-1',
              },
              {
                name: 'role-2',
                display_name: 'Role 2 for App 2, Namespace 1',
                resource_url: 'https://localhost/guardian/management/roles/app-2/namespace-1/role-2',
                app_name: 'app-2',
                namespace_name: 'namespace-1',
              },
              {
                name: 'role-1',
                display_name: 'Role 1 for App 2, Namespace 2',
                resource_url: 'https://localhost/guardian/management/roles/app-2/namespace-2/role-1',
                app_name: 'app-2',
                namespace_name: 'namespace-2',
              },
              {
                name: 'role-2',
                display_name: 'Role 2 for App 2, Namespace 2',
                resource_url: 'https://localhost/guardian/management/roles/app-2/namespace-2/role-2',
                app_name: 'app-2',
                namespace_name: 'namespace-2',
              },
            ],
          });
        case 'api':
          return new ApiDataAdapter(
            authenticationAdapter,
            config.dataPort.apiConfig.uri,
            config.dataPort.apiConfig.useProxy
          );
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
