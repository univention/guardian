/*
import {defineStore} from 'pinia';
import {ref} from 'vue';
import Keycloak from 'keycloak-js';
import {config} from '@/helpers/config';
import router from '@/router';


class NotAuthenticatedError extends Error {
  constructor() {
    super('Please authenticate first');

    // Set the prototype explicitly.
    Object.setPrototypeOf(this, NotAuthenticatedError.prototype);
  }
}


class Login {

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

}

export const useLoginStore = defineStore('login', () => {

  let authenticatePromise: (null | Promise<boolean>) = null;
  const login = new Login();

  const username = ref();
  const authenticated = ref(false);

  const authenticate = async function(): Promise<boolean> {
    if (authenticatePromise === null) {
      authenticatePromise = login.authenticate();
    }
    authenticated.value = await authenticatePromise;
    username.value = login.username;
    return authenticated.value;
  };

  const getValidAuthorizationHeader = async function(minTokenValidity = 30): Promise<({Authorization: string} | Record<string, never>)> {
    if (!login.authenticated) {
      await authenticate();
    }
    await login.updateToken(minTokenValidity); // keycloak-js already ensures only one token refresh request runs at a time
    return login.authorizationHeader;
  };

  return {
    username,
    authenticate,
    authenticated,
    getValidAuthorizationHeader,
  };

});
*/
