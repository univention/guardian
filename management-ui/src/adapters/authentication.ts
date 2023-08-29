import type {AuthenticationPort, AuthenticationSuccess} from '@/ports/authentication';

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

/*
export default class KeycloakAuthenticationAdapter {

  #keycloak;

  constructor() {
    // https://www.keycloak.org/docs/latest/securing_apps/index.html#_javascript_adapter
    this.#keycloak = new Keycloak({
      url: config.ssoURI,
      realm: 'ucs',
      clientId: 'ucs-school-ui-users',
    });
  }

  authenticate(): Promise<boolean> {
    // Todo: if already authenticated, do we want to force it? Maybe just return
    // yes if authenticated
    const requestedRoute = router.resolve(router.currentRoute.value.path);
    const redirectRoute = requestedRoute.matched.length ? requestedRoute : router.resolve({name: 'list'});
    const authenticate = this.#keycloak.init({
      onLoad: 'login-required',
      checkLoginIframe: false, // This only works if the app is in tne frame-ancestor list in keycloak
      pkceMethod: 'S256',
      redirectUri: new URL(redirectRoute.href, window.location.origin).href,
    });
    authenticate.then(success => {
      if (success === true) {
        // Clear oauth related hashtags from vue route
        router.replace(router.currentRoute.value.path);
      }
    });
    return authenticate;
  }

  updateToken(minTokenValidity = 5): Promise<boolean> {
    return this.#keycloak.updateToken(minTokenValidity);
  }

  get authorizationHeader(): {Authorization: string} {
    if (this.#keycloak.token) {
      return {Authorization: `Bearer ${this.#keycloak.token}`};
    }
    throw new NotAuthenticatedError();
  }

  get authenticated(): (boolean) {
    if (this.#keycloak.authenticated !== undefined) {
      return this.#keycloak.authenticated;
    }
    return false;
  }

  get username(): (string) {
    if (this.#keycloak.idTokenParsed !== undefined && this.#keycloak.idTokenParsed['preferred_username'] !== undefined) {
      return this.#keycloak.idTokenParsed['preferred_username'];
    }
    throw new NotAuthenticatedError();
  }

  getValidAuthorizationHeader(minTokenValidity = 30): Promise<({Authorization: string} | Record<string, never>)> {
    if (!login.authenticated) {
      await authenticate();
    }
    await login.updateToken(minTokenValidity); // keycloak-js already ensures only one token refresh request runs at a time
    return login.authorizationHeader;
  };
}
*/
