<script setup lang="ts">
import {RouterView, useRouter} from 'vue-router';
import {ref, onMounted} from 'vue';
import {useErrorStore} from '@/stores/error';
import {useAdapterStore} from '@/stores/adapter';
import {useSettingsStore} from '@/stores/settings';
import {useTranslation} from 'i18next-vue';
import {UStandbyFullScreen, UConfirmDialog} from '@univention/univention-veb';

const loading = ref(true);
const errors = useErrorStore();
const {t} = useTranslation();
const router = useRouter();

onMounted(async () => {
  try {
    const settingsStore = useSettingsStore();
    await settingsStore.init();

    const adapterStore = useAdapterStore(settingsStore.config);
    // We need to wait until the routes are loaded;
    // otherwise, login will always redirect back to '/',
    // instead of the requested route.
    await router.isReady();
    const isAuthenticated = await adapterStore.authenticationAdapter.authenticate();
    if (!isAuthenticated) {
      errors.push({
        title: t('ErrorModal.heading'),
        message: t('App.error.loginFailed'),
        unRecoverable: true,
      });
    }
  } catch (error) {
    console.log(error);
    errors.push({
      title: t('ErrorModal.heading'),
      message: t('App.error.config'),
      unRecoverable: true,
    });
    loading.value = false;
    return;
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
