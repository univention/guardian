<script setup lang="ts">
import {ref, type Ref, onMounted} from 'vue';
import {useRoute, useRouter} from 'vue-router';
import {UButton, UInputText} from '@univention/univention-veb';
import type {AuthenticationPort, AuthenticationSuccess} from '@/ports/authentication';
import {InMemoryAuthenticationAdapter, KeycloakAuthenticationAdapter} from '@/adapters/authentication';
import {useSettingsStore} from '@/stores/settings';
import {useAdapterStore} from '@/stores/adapter';
import SettingsConfig from '@/tests/components/SettingsConfig.vue';

const loading = ref(true);
const router = useRouter();
const route = useRoute();
const settingsStore = useSettingsStore();

interface Error {
  error: string;
}

interface TestAdapter {
  name: string;
  adapter: AuthenticationPort;
  token: AuthenticationSuccess | Error | null;
  error: string;
}

// Testing globally configured Keycloak Adapter.
// This is configured with a dummy adapter that gets updated during onMounted.
const configuredAdapter: TestAdapter = {
  name: 'configured',
  adapter: new KeycloakAuthenticationAdapter('', '', ''),
  token: null,
  error: '',
};

// Testing manually configured Keycloak Adapter
const keycloakSsoUri = ref('https://ucs-sso-ng.school.test');
const keycloakRealm = ref('ucs');
const keycloakClientId = ref('guardian-management-ui-dev');
const keycloakAdapter: TestAdapter = {
  name: 'keycloak',
  adapter: new KeycloakAuthenticationAdapter(keycloakSsoUri.value, keycloakRealm.value, keycloakClientId.value),
  token: null,
  error: '',
};

// Testing mock adapter when we can log in and out
const authenticatedInMemoryAdapter: TestAdapter = {
  name: 'authenticatedInMemory',
  adapter: new InMemoryAuthenticationAdapter('test-user', true),
  token: null,
  error: '',
};

// Testing mock adapter when login fails to function
const unauthenticatedInMemoryAdapter: TestAdapter = {
  name: 'unauthenticatedInMemory',
  adapter: new InMemoryAuthenticationAdapter('', false),
  token: null,
  error: '',
};

// This controls the actual display
const currentAdapter: Ref<TestAdapter | null> = ref(null);

const switchToAuthenticatedAdapter = () => {
  currentAdapter.value = authenticatedInMemoryAdapter;
  let queryParams = {...route.query};
  queryParams.adapter = authenticatedInMemoryAdapter.name;
  router.push({name: 'testsAuthenticationAdapter', query: queryParams});
};
const switchToUnauthenticatedAdapter = () => {
  currentAdapter.value = unauthenticatedInMemoryAdapter;
  let queryParams = {...route.query};
  queryParams.adapter = unauthenticatedInMemoryAdapter.name;
  router.push({name: 'testsAuthenticationAdapter', query: queryParams});
};
const switchToKeycloakAdapter = () => {
  currentAdapter.value = keycloakAdapter;
  let queryParams = {...route.query};
  queryParams.adapter = keycloakAdapter.name;
  router.push({name: 'testsAuthenticationAdapter', query: queryParams});
};
const switchToConfiguredAdapter = () => {
  currentAdapter.value = configuredAdapter;
  let queryParams = {...route.query};
  queryParams.adapter = configuredAdapter.name;
  router.push({name: 'testsAuthenticationAdapter', query: queryParams});
};

const login = async () => {
  if (currentAdapter.value !== null) {
    // If we're using a router that redirects to an SSO, this will help us
    // re-initialize when we come back
    await router.replace({query: {redirectLogin: 'true', ...route.query}});

    let success = await currentAdapter.value.adapter.authenticate();
    if (!success) {
      currentAdapter.value.token = null;
      currentAdapter.value.error = 'Unable to log in';
      return;
    }

    // We don't need to redirect to adapter login any more
    let queryParams = {...route.query};
    delete queryParams.redirectLogin;
    await router.replace({query: queryParams});
  }
};

const logout = async () => {
  if (currentAdapter.value !== null) {
    await currentAdapter.value.adapter.logout();
    currentAdapter.value.token = null;
    currentAdapter.value.error = '';
  }
};

const getAuthorizationHeader = async () => {
  if (currentAdapter.value !== null) {
    // If we're using a router that redirects to an SSO, this will help us
    // re-initialize when we come back
    await router.replace({
      query: {
        redirectLogin: 'true',
        getAuthorizationHeader: 'true',
        ...route.query,
      },
    });

    try {
      currentAdapter.value.token = await currentAdapter.value.adapter.getValidAuthorizationHeader();
    } catch (error) {
      console.log(error);
      currentAdapter.value.token = {error: 'Unable to authenticate'};
    }

    // We don't need to redirect to adapter login any more
    let queryParams = {...route.query};
    delete queryParams.redirectLogin;
    delete queryParams.getAuthorizationHeader;
    await router.replace({query: queryParams});
  }
};

const updateKeycloakSettings = async () => {
  if (currentAdapter.value?.name === 'keycloak') {
    await router.push({
      name: 'testsAuthenticationAdapter',
      query: {
        adapter: 'keycloak',
        keycloakSsoUri: keycloakSsoUri.value,
        keycloakRealm: keycloakRealm.value,
        keycloakClientId: keycloakClientId.value,
      },
    });

    if (currentAdapter.value.adapter.authenticated) {
      await logout();
    } else {
      currentAdapter.value.adapter = new KeycloakAuthenticationAdapter(
        keycloakSsoUri.value,
        keycloakRealm.value,
        keycloakClientId.value
      );
    }
  }
};

onMounted(async () => {
  await settingsStore.init();
  const adapterStore = useAdapterStore(settingsStore.config);
  configuredAdapter.adapter = adapterStore.authenticationAdapter;

  let startingAdapter = (() => {
    switch (route.query.adapter) {
      case 'authenticatedInMemory':
        return authenticatedInMemoryAdapter;
      case 'unauthenticatedInMemory':
        return unauthenticatedInMemoryAdapter;
      case 'keycloak':
        return keycloakAdapter;
      default:
        return configuredAdapter;
    }
  })();
  currentAdapter.value = startingAdapter;

  // If one keycloak setting is present, we expect all of them to be present,
  // unless someone manually changed the querystring.
  if (
    typeof route.query.keycloakSsoUri === 'string' &&
    typeof route.query.keycloakRealm === 'string' &&
    typeof route.query.keycloakClientId === 'string'
  ) {
    keycloakAdapter.adapter = new KeycloakAuthenticationAdapter(
      route.query.keycloakSsoUri,
      route.query.keycloakRealm,
      route.query.keycloakClientId
    );

    keycloakSsoUri.value = route.query.keycloakSsoUri;
    keycloakRealm.value = route.query.keycloakRealm;
    keycloakClientId.value = route.query.keycloakClientId;
  }
  if (route.query.getAuthorizationHeader !== undefined) {
    currentAdapter.value.token = await currentAdapter.value.adapter.getValidAuthorizationHeader();

    // We don't need to fetch the authorization header anymore
    let queryParams = {...route.query};
    delete queryParams.redirectLogin;
    delete queryParams.getAuthorizationHeader;
    await router.replace({query: queryParams});
  } else if (route.query.redirectLogin !== undefined) {
    await currentAdapter.value.adapter.authenticate();

    // We don't need to redirect to adapter login anymore
    let queryParams = {...route.query};
    delete queryParams.redirectLogin;
    await router.replace({query: queryParams});
  }

  loading.value = false;
});
</script>

<template>
  <main v-if="!loading" class="testView">
    <h1><RouterLink :to="{name: 'testsMain'}">Manual Tests</RouterLink></h1>
    <h2>Authentication Adapter Tests</h2>

    <div class="testButtonsWrapper">
      <div class="testButtons">
        <UButton
          type="button"
          label="Configured Global Adapter"
          :class="{'uButton--flat': currentAdapter?.name !== 'configured'}"
          @click="switchToConfiguredAdapter"
        />
        <UButton
          type="button"
          label="Keycloak Adapter"
          :class="{'uButton--flat': currentAdapter?.name !== 'keycloak'}"
          @click="switchToKeycloakAdapter"
        />
        <UButton
          type="button"
          label="InMemory Adapter, Logs In"
          :class="{'uButton--flat': currentAdapter?.name !== 'authenticatedInMemory'}"
          @click="switchToAuthenticatedAdapter"
        />
        <UButton
          type="button"
          label="InMemory Adapter, Blocks Login"
          :class="{'uButton--flat': currentAdapter?.name !== 'unauthenticatedInMemory'}"
          @click="switchToUnauthenticatedAdapter"
        />
      </div>
    </div>
    <p v-show="currentAdapter?.name === 'configured'">Verify the setup for the current globally configured adapter.</p>
    <p v-show="currentAdapter?.name === 'keycloak'">Test a manually configured keycloak instance</p>
    <p v-show="currentAdapter?.name === 'authenticatedInMemory'">Test mock adapter that can log in and out</p>
    <p v-show="currentAdapter?.name === 'unauthenticatedInMemory'">Test mock adapter that is unable to log in</p>

    <div class="testWrapper">
      <div
        v-if="currentAdapter?.name !== 'keycloak' || settingsStore.config.authenticationPort.adapter !== 'keycloak'"
        class="uContainer uCard test-container"
      >
        <h3>Login/Logout:</h3>
        <table class="testValues">
          <tr>
            <td><label class="testLabel">username:</label></td>
            <td>{{ currentAdapter?.adapter.username }}</td>
          </tr>
          <tr>
            <td><label class="testLabel">isAuthenticated:</label></td>
            <td>{{ currentAdapter?.adapter.authenticated }}</td>
          </tr>
        </table>

        <UButton v-show="!currentAdapter?.adapter.authenticated" type="button" label="Login" @click="login" />

        <UButton v-show="currentAdapter?.adapter.authenticated" type="button" label="Logout" @click="logout" />
        <p class="error">{{ currentAdapter?.error }}</p>

        <h3>Authorization Header:</h3>
        <UButton type="button" label="Get Authorization Header" @click="getAuthorizationHeader" />

        <p class="token">{{ currentAdapter?.token }}</p>
      </div>

      <div v-if="currentAdapter?.name === 'keycloak'" class="uContainer uCard">
        <h3>Update Adapter Configuration</h3>
        <template v-if="settingsStore.config.authenticationPort.adapter === 'keycloak'">
          <p>
            NOTE: These tests are currently disabled because there is already one keycloak adapter configured for this
            app.
          </p>
          <p>
            If you would like to run tests on a manually-configured Keycloak adapter, please update your .env file to
            use the 'in_memory' adapter.
          </p>
        </template>
        <template v-else>
          <UInputText
            v-model="keycloakSsoUri"
            name="keycloak-sso-uri"
            label="SSO URI"
            description="The URI to use for Keycloak SSO"
          />
          <UInputText
            v-model="keycloakRealm"
            name="keycloak-realm"
            label="Realm"
            description="The Keycloak realm to use"
          />
          <UInputText
            v-model="keycloakClientId"
            name="keycloak-client-id"
            label="Client ID"
            description="The client ID to use when talking to Keycloak"
          />

          <UButton type="button" label="Update Adapter Settings and Logout" @click="updateKeycloakSettings" />
        </template>
      </div>

      <div v-if="currentAdapter?.name === 'configured'" class="uContainer uCard">
        <h3>Current Settings</h3>
        <SettingsConfig :configObj="settingsStore.config.authenticationPort" />
      </div>
    </div>
  </main>
</template>

<style lang="stylus">
main.testView
  .token
    word-wrap: anywhere
    max-width: 50ch
</style>
