<script setup lang="ts">
import {ref, onMounted} from 'vue';
import {UButton} from '@univention/univention-veb';
import {useSettingsStore} from '@/stores/settings';
import SettingsConfig from '@/tests/components/SettingsConfig.vue';

const loading = ref(true);

const configuredAdapter = import.meta.env.VITE__MANAGEMENT_UI__ADAPTER__SETTINGS_PORT;
const settingsStore = useSettingsStore();
const config = ref(settingsStore.config);
const currentAdapter = ref('configured');

const switchToConfiguredAdapter = async () => {
  currentAdapter.value = 'configured';
  await settingsStore.init(configuredAdapter, true);
};
const switchToEnvAdapter = async () => {
  currentAdapter.value = 'env';
  await settingsStore.init('env', true);
};
const switchToUrlAdapter = async () => {
  currentAdapter.value = 'url';
  await settingsStore.init('url', true);
};

onMounted(async () => {
  await settingsStore.init();
  loading.value = false;
});
</script>

<template>
  <template></template>
  <main
    v-if="!loading"
    class="testView"
  >
    <h1><RouterLink :to="{name: 'testsMain'}">Manual Tests</RouterLink></h1>

    <h2>Settings Adapter Tests</h2>

    <div class="testButtonsWrapper">
      <UButton
        :class="{'uButton--flat': currentAdapter !== 'configured'}"
        type="button"
        label="Configured Global Adapter"
        @click="switchToConfiguredAdapter"
      />
      <UButton
        :class="{'uButton--flat': currentAdapter !== 'env'}"
        type="button"
        label="Env Adapter"
        @click="switchToEnvAdapter"
      />
      <UButton
        :class="{'uButton--flat': currentAdapter !== 'config'}"
        type="button"
        label="Config Adapter"
        @click="switchToUrlAdapter"
      />
    </div>
    <p>Verify settings for the currently configured adapter for the app</p>

    <div class="uContainer uCard">
      <SettingsConfig :configObj="config" />
    </div>
  </main>
</template>
