import Keycloak from 'keycloak-js';
import type {AuthenticationPort, AuthenticationSuccess} from '@/ports/authentication';
import router from '@/router';

class NotAuthenticatedError extends Error {
  constructor() {
    super('Please authenticate first');

    // Set the prototype explicitly.
    Object.setPrototypeOf(this, NotAuthenticatedError.prototype);
  }
}

export const inMemoryAuthenticationSettings = {
  isAuthenticated: 'inMemoryAuthenticationAdapter.isAuthenticated',
  username: 'inMemoryAuthenticationAdapter.username',
};

export class InMemoryAuthenticationAdapter implements AuthenticationPort {
  authenticated: boolean;
  username: string;

  private _configuredUsername: string;
  private _configuredAuthenticated: boolean;

  constructor(username: string, isAuthenticated: boolean) {
    this._configuredUsername = username;
    this._configuredAuthenticated = isAuthenticated;
    this.username = '';
    this.authenticated = false;
  }

  authenticate(): Promise<boolean> {
    this.authenticated = this._configuredAuthenticated;
    this.username = this._configuredAuthenticated ? this._configuredUsername : '';
    return new Promise(resolve => {
      resolve(this.authenticated);
    });
  }

  async getValidAuthorizationHeader(minTokenValidity: number = 30): Promise<AuthenticationSuccess> {
    if (!this.authenticated) {
      if (!(await this.authenticate())) {
        throw new NotAuthenticatedError();
      }
    }

    return new Promise(resolve => {
      resolve({Authorization: `test-token-${minTokenValidity}`});
    });
  }

  logout(): Promise<boolean> {
    this.authenticated = false;
    this.username = '';
    return new Promise(resolve => {
      resolve(true);
    });
  }
}

export const keycloakAuthenticationSettings = {
  ssoUri: 'keycloakAuthenticationAdapter.ssoUri',
  realm: 'keycloakAuthenticationAdapter.realm',
  clientId: 'keycloakAuthenticationAdapter.clientId',
};

export class KeycloakAuthenticationAdapter {
  private _keycloak: Keycloak;
  private readonly _ssoUri: string;
  private readonly _realm: string;
  private readonly _clientId: string;

  constructor(ssoUri: string, realm: string, clientId?: string) {
    this._ssoUri = ssoUri;
    this._realm = realm;
    this._clientId = clientId ?? 'guardian-management-ui';
    this._keycloak = new Keycloak({
      url: this._ssoUri,
      realm: this._realm,
      clientId: this._clientId,
    });
  }

  async authenticate(): Promise<boolean> {
    const requestedRoute = router.resolve(router.currentRoute.value.fullPath);
    const redirectRoute = requestedRoute.matched.length ? requestedRoute : router.resolve({name: 'landing'});
    const redirectUri = new URL(redirectRoute.href, window.location.origin).href;

    let success = false;
    try {
      success = await this._keycloak.init({
        onLoad: 'login-required',
        checkLoginIframe: false, // This only works if the app is in the frame-ancestor list in keycloak
        pkceMethod: 'S256',
        redirectUri: redirectUri,
      });
    } catch (error) {
      // This most likely means we're already initialized; let's try a login instead
      console.log(`DEBUG: ${error}`);
      await this._keycloak.login({redirectUri: redirectUri});
      success = true;
    }

    return new Promise(resolve => {
      resolve(success);
    });
  }

  updateToken(minTokenValidity: number): Promise<boolean> {
    return this._keycloak.updateToken(minTokenValidity);
  }

  get authorizationHeader(): {Authorization: string} {
    if (this._keycloak.token) {
      return {Authorization: `Bearer ${this._keycloak.token}`};
    }
    // If this is called through getValidAuthorizationHeader,
    // we don't expect this error
    throw new NotAuthenticatedError();
  }

  async getValidAuthorizationHeader(minTokenValidity: number = 30): Promise<AuthenticationSuccess> {
    if (!this.authenticated) {
      if (!(await this.authenticate())) {
        throw new NotAuthenticatedError();
      }
    }

    // keycloak-js already ensures only one token refresh request runs at a time
    await this.updateToken(minTokenValidity);
    return this.authorizationHeader;
  }

  async logout(): Promise<boolean> {
    const requestedRoute = router.resolve(router.currentRoute.value.fullPath);
    const redirectRoute = requestedRoute.matched.length ? requestedRoute : router.resolve({name: 'landing'});
    const redirectUri = new URL(redirectRoute.href, window.location.origin).href;

    try {
      await this._keycloak.logout({redirectUri: redirectUri});
    } catch (error) {
      // We are probably already logged out
      console.log(`DEBUG: ${error}`);
      return new Promise(resolve => {
        resolve(false);
      });
    }

    return new Promise(resolve => {
      resolve(true);
    });
  }

  get authenticated(): boolean {
    if (this._keycloak.authenticated !== undefined) {
      try {
        return this._keycloak.authenticated;
      } catch (error) {
        // Most likely "Please authenticate first"
        console.log(`DEBUG: ${error}`);
        return false;
      }
    }
    return false;
  }

  get username(): string {
    if (
      this._keycloak.idTokenParsed !== undefined &&
      this._keycloak.idTokenParsed['preferred_username'] !== undefined
    ) {
      try {
        return this._keycloak.idTokenParsed['preferred_username'];
      } catch (error) {
        // Most likely "Please authenticate first"
        console.log(`DEBUG: ${error}`);
        return '';
      }
    }
    return '';
  }
}
