<script setup lang="ts">
import {ref, onMounted} from 'vue';
import {UButton} from '@univention/univention-veb';
import {useSettingsStore} from '@/stores/settings';
import SettingsConfig from '@/tests/components/SettingsConfig.vue';

const loading = ref(true);

const settingsStore = useSettingsStore();

onMounted(async () => {
  await settingsStore.init();
  loading.value = false;
});
</script>

<template>
  <template></template>
  <main v-if="!loading" class="testView">
    <h1><RouterLink :to="{name: 'testsMain'}">Manual Tests</RouterLink></h1>

    <h2>Settings Adapter Tests</h2>

    <div class="testButtonsWrapper">
      <UButton type="button" label="Configured Global Adapter" />
    </div>
    <p>Verify settings for the currently configured adapter for the app</p>

    <div class="uContainer uCard">
      <SettingsConfig :configObj="settingsStore.config" />
    </div>
  </main>
</template>
