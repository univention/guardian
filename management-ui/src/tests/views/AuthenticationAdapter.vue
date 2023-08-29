<script setup lang="ts">
import {ref, onMounted} from 'vue';
import {UButton} from '@univention/univention-veb';
import type {AuthenticationPort, AuthenticationSuccess} from '@/ports/authentication';
import {InMemoryAuthenticationAdapter} from '@/adapters/authentication';

const loading = ref(true);

interface Error {
  error: string;
}

interface TestAdapter {
  name: string;
  adapter: AuthenticationPort;
  token: AuthenticationSuccess | Error | null;
  error: string;
}

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
const currentAdapter = ref(authenticatedInMemoryAdapter);

const useAuthenticatedAdapter = () => {
  currentAdapter.value = authenticatedInMemoryAdapter;
};
const useUnauthenticatedAdapter = () => {
  currentAdapter.value = unauthenticatedInMemoryAdapter;
};

const login = async () => {
  let success = await currentAdapter.value.adapter.authenticate();
  if (!success) {
    currentAdapter.value.token = null;
    currentAdapter.value.error = 'Unable to log in';
    return;
  }
};

const logout = async () => {
  await currentAdapter.value.adapter.logout();
  currentAdapter.value.token = null;
  currentAdapter.value.error = '';
};

const getAuthorizationHeader = async () => {
  try {
    currentAdapter.value.token = await currentAdapter.value.adapter.getValidAuthorizationHeader();
  } catch (error) {
    console.log(error);
    currentAdapter.value.token = {error: 'Unable to authenticate'};
  }
};

onMounted(async () => {
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
          label="InMemory Adapter, Logs In"
          :class="{'uButton--flat': currentAdapter.name !== 'authenticatedInMemory'}"
          @click="useAuthenticatedAdapter"
        />
        <UButton
          type="button"
          label="InMemory Adapter, Blocks Login"
          :class="{'uButton--flat': currentAdapter.name !== 'unauthenticatedInMemory'}"
          @click="useUnauthenticatedAdapter"
        />
      </div>
    </div>
    <p v-show="currentAdapter.name === 'authenticatedInMemory'">
      Test description: Test mock adapter that can log in and out
    </p>
    <p v-show="currentAdapter.name === 'unauthenticatedInMemory'">
      Test description: Test mock adapter that is unable to log in
    </p>

    <div class="uContainer uCard">
      <h3>Login/Logout:</h3>
      <table class="testValues">
        <tr>
          <td><label>username:</label></td>
          <td>{{ currentAdapter.adapter.username }}</td>
        </tr>
        <tr>
          <td><label>isAuthenticated:</label></td>
          <td>{{ currentAdapter.adapter.authenticated }}</td>
        </tr>
      </table>

      <UButton v-show="!currentAdapter.adapter.authenticated" type="button" label="Login" @click="login" />

      <UButton v-show="currentAdapter.adapter.authenticated" type="button" label="Logout" @click="logout" />
      <p class="error">{{ currentAdapter.error }}</p>

      <h3>Authorization Header:</h3>
      <UButton type="button" label="Get Authorization Header" @click="getAuthorizationHeader" />

      <p>{{ currentAdapter.token }}</p>
    </div>
  </main>
</template>

<style lang="stylus">
main.testView
  padding: calc(4 * var(--layout-spacing-unit))
  margin: 0 auto
  height: 100vh
  display: flex
  flex-direction: column
  align-items: flex-start
  gap: var(--layout-spacing-unit)

  label
    font-weight: bold
    padding-right: calc(2 * var(--layout-spacing-unit))

  h3
    margin-top: calc(2 * var(--layout-spacing-unit))

  .error
    color: var(--font-color-error)

  .uContainer
    > .uButton
      margin: calc(2 * var(--layout-spacing-unit)) 0

  .testButtonsWrapper
    display: flex
    margin: calc(2 * var(--layout-spacing-unit)) 0

  .testButtons
    display: flex
    border: 1px solid var(--font-color-contrast-low)
    border-radius: var(--button-border-radius)
    overflow: hidden

    > .uButton
      text-decoration: none
      border-radius: 0
      padding: 0 calc(2 * var(--layout-spacing-unit))
</style>
