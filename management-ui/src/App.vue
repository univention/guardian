<script setup lang="ts">
import {RouterView} from 'vue-router';
import {ref, onMounted} from 'vue';
import {config} from '@/helpers/config';
// import {useLoginStore} from '@/stores/login';
import {useErrorStore} from '@/stores/error';
import {useTranslation} from 'i18next-vue';
import {UStandbyFullScreen, UConfirmDialog} from '@univention/univention-veb';

const loading = ref(true);
const errors = useErrorStore();

interface Config {
  backendURL: string;
  ssoURI: string;
  ucsWebTheme: string;
  searchLimit: number;
}

const {t} = useTranslation();

onMounted(async () => {
  if (import.meta.env.PROD || import.meta.env.VITE_USE_REAL_BACKEND === 'true') {
    const answer = await fetch(`${import.meta.env.BASE_URL}/config.json`, {
      headers: {
        Accept: 'application/json',
      },
    });
    try {
      const json = (await answer.json()) as Config;
      config.backendURL = json.backendURL;
      config.ssoURI = json.ssoURI;
      config.ucsWebTheme = json.ucsWebTheme;
      config.searchLimit = json.searchLimit;
    } catch (error) {
      errors.push({
        title: t('ErrorModal.heading'),
        message: t('App.error.config'),
        unRecoverable: true,
      });
      loading.value = false;
      return;
    }
    /*
    const loginStore = useLoginStore();
    if (!loginStore.authenticated) {
      const success = await loginStore.authenticate();
      if (!success) {
        errors.push({
          title: t('ErrorModal.heading'),
          message: t('App.error.loginFailed'),
          unRecoverable: true,
        });
        loading.value = false;
        return;
      }
    }
    */
    document.documentElement.className = `theme-${config.ucsWebTheme}`;
  }
  loading.value = false;
});
</script>

<template>
  <UStandbyFullScreen :active="loading" />
  <template v-if="!loading">
    <div v-if="errors.activeError && errors.activeError.unRecoverable" class="app__errorMessage">
      <div class="uCard uContainer">
        <h1 v-if="errors.activeError.title">
          {{ errors.activeError.title }}
        </h1>
        {{ errors.activeError.message }}
      </div>
    </div>
    <RouterView v-else v-slot="{Component}">
      <KeepAlive :include="['ListView']">
        <component :is="Component" />
      </KeepAlive>
      <UConfirmDialog
        :active="!!errors.activeError"
        :title="errors.activeError?.title || t('ErrorModal.heading')"
        :confirmLabel="t('ErrorModal.button.confirmation')"
        hideCancel
        @confirm="errors.advance"
      >
        <template #description>
          <p>{{ errors.activeError?.message }}</p>
        </template>
      </UConfirmDialog>
    </RouterView>
  </template>
</template>

<style lang="stylus">
.app__errorMessage
  position: fixed
  inset: 0
  display: flex
  align-items: center
  justify-content: center
  padding: calc(2 * var(--layout-spacing-unit))
</style>
