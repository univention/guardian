<script setup lang="ts">
import {ref, onMounted} from 'vue';

const loading = ref(true);

onMounted(async () => {
  loading.value = false;
});
</script>

<template>
  <main v-if="!loading" class="testView">
    <h1><RouterLink :to="{name: 'testsMain'}">Manual Tests</RouterLink></h1>

    <h2>Adapter Tests</h2>
    <ul>
      <li><RouterLink :to="{name: 'testsSettingsAdapter'}">Settings Adapter Tests</RouterLink></li>
      <li><RouterLink :to="{name: 'testsAuthenticationAdapter'}">Authentication Adapter Tests</RouterLink></li>
      <li><RouterLink :to="{name: 'testsDataAdapter'}">Data Adapter Tests</RouterLink></li>
    </ul>
  </main>
</template>

<style lang="stylus">
@require '../assets/style.styl';
</style>
